"""Unit tests for CursorOrderIterator, the concrete GoF Iterator."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from order_pagination.domain.entities import Order
from order_pagination.domain.interfaces import OrderRepository
from order_pagination.infrastructure.cursor_iterator import CursorOrderIterator


class FakeOrderRepository(OrderRepository):
    """An in-memory OrderRepository that paginates a fixed list of orders."""

    def __init__(self, total: int) -> None:
        now = datetime(2026, 1, 1, tzinfo=UTC)
        self._orders = [
            Order(order_id=i, customer=f"c-{i}", amount=float(i), created_at=now)
            for i in range(1, total + 1)
        ]
        self.fetch_calls = 0

    def fetch_page(
        self, cursor: str | None, limit: int
    ) -> tuple[list[Order], str | None]:
        self.fetch_calls += 1
        last_id = int(cursor) if cursor is not None else 0
        page = [o for o in self._orders if o.order_id > last_id][:limit]
        next_cursor = str(page[-1].order_id) if len(page) == limit else None
        return page, next_cursor


def test_iterates_every_order_exactly_once() -> None:
    repository = FakeOrderRepository(total=7)
    iterator = CursorOrderIterator(repository, page_size=3)

    seen = []
    while iterator.has_next():
        seen.append(iterator.next().order_id)

    assert seen == [1, 2, 3, 4, 5, 6, 7]


def test_fetches_pages_lazily_not_all_at_once() -> None:
    repository = FakeOrderRepository(total=10)
    iterator = CursorOrderIterator(repository, page_size=4)

    iterator.next()  # triggers first page load only

    assert repository.fetch_calls == 1


def test_has_next_is_false_for_empty_collection() -> None:
    repository = FakeOrderRepository(total=0)
    iterator = CursorOrderIterator(repository, page_size=10)

    assert iterator.has_next() is False


def test_next_raises_stop_iteration_when_exhausted() -> None:
    repository = FakeOrderRepository(total=1)
    iterator = CursorOrderIterator(repository, page_size=10)
    iterator.next()

    with pytest.raises(StopIteration):
        iterator.next()


def test_has_next_is_idempotent() -> None:
    repository = FakeOrderRepository(total=2)
    iterator = CursorOrderIterator(repository, page_size=10)

    assert iterator.has_next() is True
    assert iterator.has_next() is True
    assert iterator.next().order_id == 1
