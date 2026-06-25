"""Use cases orchestrating paginated listing and full-collection export."""

from __future__ import annotations

from collections.abc import Iterator as TypingIterator

from order_pagination.domain.entities import Order, OrdersPage
from order_pagination.domain.interfaces import OrderRepository
from order_pagination.infrastructure.cursor_iterator import CursorOrderIterator


class ListOrdersPageUseCase:
    """Returns a single page of orders — the typical REST pagination request."""

    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def execute(self, cursor: str | None, limit: int) -> OrdersPage:
        items, next_cursor = self._repository.fetch_page(cursor, limit)
        return OrdersPage(items=items, next_cursor=next_cursor)


class ExportAllOrdersUseCase:
    """Streams every order in the collection using the GoF Iterator directly.

    Unlike `ListOrdersPageUseCase`, the caller never sees cursors — it just
    consumes orders one at a time until the iterator is exhausted, while
    pages are fetched lazily under the hood.
    """

    def __init__(self, repository: OrderRepository, page_size: int = 100) -> None:
        self._repository = repository
        self._page_size = page_size

    def execute(self) -> TypingIterator[Order]:
        iterator = CursorOrderIterator(self._repository, self._page_size)
        while iterator.has_next():
            yield iterator.next()
