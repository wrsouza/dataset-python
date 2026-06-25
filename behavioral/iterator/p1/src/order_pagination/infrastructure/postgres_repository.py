"""PostgreSQL-backed implementation of OrderRepository using keyset pagination."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from order_pagination.domain.entities import Order
from order_pagination.domain.interfaces import OrderRepository

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
)
"""

SELECT_PAGE_SQL = """
SELECT order_id, customer, amount, created_at
FROM orders
WHERE order_id > %s
ORDER BY order_id ASC
LIMIT %s
"""


class DBConnection(Protocol):
    """Minimal DB-API connection contract this repository relies on."""

    def cursor(self) -> Any: ...

    def commit(self) -> None: ...


class PostgresOrderRepository(OrderRepository):
    """Fetches orders page by page using `order_id` as a keyset cursor."""

    def __init__(self, connection: DBConnection) -> None:
        self._connection = connection
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        cursor = self._connection.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        self._connection.commit()

    def fetch_page(
        self, cursor: str | None, limit: int
    ) -> tuple[list[Order], str | None]:
        last_id = int(cursor) if cursor is not None else 0
        db_cursor = self._connection.cursor()
        db_cursor.execute(SELECT_PAGE_SQL, (last_id, limit))
        rows = db_cursor.fetchall()

        orders = [self._row_to_order(row) for row in rows]
        next_cursor = str(orders[-1].order_id) if len(orders) == limit else None
        return orders, next_cursor

    @staticmethod
    def _row_to_order(row: tuple[Any, ...]) -> Order:
        order_id, customer, amount, created_at = row
        return Order(
            order_id=order_id,
            customer=customer,
            amount=float(amount),
            created_at=(
                created_at
                if isinstance(created_at, datetime)
                else datetime.fromisoformat(created_at)
            ),
        )
