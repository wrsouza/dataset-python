"""Unit tests for PostgresOrderRepository using a fake DB-API connection."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from order_pagination.infrastructure.postgres_repository import PostgresOrderRepository


class FakeCursor:
    def __init__(self, rows: list[tuple[Any, ...]]) -> None:
        self._rows = rows
        self._result: list[tuple[Any, ...]] = []

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        statement = sql.strip()
        if statement.startswith("CREATE TABLE"):
            return
        last_id, limit = params
        self._result = [row for row in self._rows if row[0] > last_id][:limit]

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self._result


class FakeConnection:
    def __init__(self, rows: list[tuple[Any, ...]]) -> None:
        self._rows = rows

    def cursor(self) -> FakeCursor:
        return FakeCursor(self._rows)

    def commit(self) -> None:
        pass


def _rows(count: int) -> list[tuple[Any, ...]]:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return [(i, f"customer-{i}", 10.0 * i, now) for i in range(1, count + 1)]


def test_fetch_page_returns_next_cursor_when_full_page() -> None:
    repository = PostgresOrderRepository(FakeConnection(_rows(5)))

    orders, next_cursor = repository.fetch_page(None, limit=2)

    assert [o.order_id for o in orders] == [1, 2]
    assert next_cursor == "2"


def test_fetch_page_returns_none_cursor_on_last_partial_page() -> None:
    repository = PostgresOrderRepository(FakeConnection(_rows(5)))

    orders, next_cursor = repository.fetch_page("4", limit=2)

    assert [o.order_id for o in orders] == [5]
    assert next_cursor is None


def test_fetch_page_returns_empty_list_past_the_end() -> None:
    repository = PostgresOrderRepository(FakeConnection(_rows(3)))

    orders, next_cursor = repository.fetch_page("3", limit=10)

    assert orders == []
    assert next_cursor is None


def test_fetch_page_maps_rows_to_orders() -> None:
    repository = PostgresOrderRepository(FakeConnection(_rows(1)))

    orders, _ = repository.fetch_page(None, limit=1)

    assert orders[0].customer == "customer-1"
    assert orders[0].amount == 10.0
