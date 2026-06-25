from __future__ import annotations

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

_engine: Engine | None = None
_SessionFactory: sessionmaker[Session] | None = None


def init_engine(database_url: str) -> None:
    """Initialize the module-level engine and session factory.

    Decision: a module-level singleton (rather than a class) keeps the
    composition root in ``main.py`` simple — call once at app startup
    (or once per test) before any ``get_session()`` call.
    """
    global _engine, _SessionFactory
    _engine = create_engine(database_url, pool_pre_ping=True)
    _SessionFactory = sessionmaker(bind=_engine)


def get_session() -> Session:
    if _SessionFactory is None:
        raise RuntimeError("Database engine not initialized. Call init_engine() first.")
    return _SessionFactory()


def create_tables(database_url: str) -> None:
    """Create application tables and seed demo inventory.

    Decision: the schema uses ``TEXT`` for the JSON-encoded order items
    column (instead of PostgreSQL's native ``JSONB``) and a portable
    ``INSERT ... WHERE NOT EXISTS`` seed statement (instead of
    ``ON CONFLICT``) so the exact same SQL also works against SQLite,
    which the integration test suite uses in place of a real PostgreSQL
    instance (see ``tests/conftest.py``).
    """
    engine = create_engine(database_url)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS inventory (
                product_id VARCHAR(64) PRIMARY KEY,
                product_name VARCHAR(255) NOT NULL,
                quantity_available INTEGER NOT NULL DEFAULT 0
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS stock_reservations (
                id VARCHAR(64) PRIMARY KEY,
                product_id VARCHAR(64) NOT NULL,
                quantity INTEGER NOT NULL,
                expires_at TIMESTAMP NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id VARCHAR(64) PRIMARY KEY,
                customer_id VARCHAR(64) NOT NULL,
                items TEXT NOT NULL,
                total_amount NUMERIC(10, 2) NOT NULL,
                status VARCHAR(32) NOT NULL,
                payment_charge_id VARCHAR(128),
                tracking_number VARCHAR(64),
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """))
        for product_id, product_name, quantity in (
            ("PROD001", "Widget Pro", 100),
            ("PROD002", "Gadget Max", 50),
            ("PROD003", "Super Gizmo", 25),
        ):
            conn.execute(
                text("""
                    INSERT INTO inventory (product_id, product_name, quantity_available)
                    SELECT :pid, :pname, :qty
                    WHERE NOT EXISTS (
                        SELECT 1 FROM inventory WHERE product_id = :pid
                    )
                """),
                {"pid": product_id, "pname": product_name, "qty": quantity},
            )
        conn.commit()
