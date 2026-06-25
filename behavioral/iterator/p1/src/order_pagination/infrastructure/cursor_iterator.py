"""Concrete Iterator: lazily walks every order, fetching pages on demand."""

from __future__ import annotations

from collections import deque

from order_pagination.domain.entities import Order
from order_pagination.domain.interfaces import OrderIterator, OrderRepository


class CursorOrderIterator(OrderIterator):
    """Traverses every order in a collection one at a time.

    Internally fetches batches of `page_size` orders from the repository
    as the buffer empties — the client only ever sees `has_next`/`next`,
    never the pagination or the underlying SQL.
    """

    def __init__(self, repository: OrderRepository, page_size: int = 100) -> None:
        self._repository = repository
        self._page_size = page_size
        self._buffer: deque[Order] = deque()
        self._cursor: str | None = None
        self._exhausted = False

    def has_next(self) -> bool:
        if not self._buffer and not self._exhausted:
            self._load_next_page()
        return bool(self._buffer)

    def next(self) -> Order:
        if not self.has_next():
            raise StopIteration("No more orders to iterate")
        return self._buffer.popleft()

    def _load_next_page(self) -> None:
        items, next_cursor = self._repository.fetch_page(self._cursor, self._page_size)
        self._buffer.extend(items)
        self._cursor = next_cursor
        if next_cursor is None:
            self._exhausted = True
