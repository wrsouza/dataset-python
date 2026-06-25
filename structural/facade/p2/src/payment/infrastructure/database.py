from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None

CREATE_TRANSACTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(64) NOT NULL,
    amount_cents INTEGER NOT NULL,
    currency VARCHAR(8) NOT NULL,
    status VARCHAR(16) NOT NULL,
    charge_id VARCHAR(64),
    failure_reason VARCHAR(255),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
)
"""


def init_engine(database_url: str) -> Engine:
    """Initialize the global SQLAlchemy engine and session factory."""
    global _engine, _SessionLocal
    _engine = create_engine(database_url, future=True)
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def create_tables(database_url: str) -> None:
    """Create the transactions table if it does not exist yet."""
    engine = _engine or create_engine(database_url, future=True)
    with engine.begin() as connection:
        connection.execute(text(CREATE_TRANSACTIONS_TABLE))


def get_session() -> Session:
    """Return a new session from the configured session factory."""
    if _SessionLocal is None:
        raise RuntimeError("init_engine() must be called before get_session()")
    return _SessionLocal()
