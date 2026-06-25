"""Abstractions for the Iterator pattern and the underlying data access."""

from __future__ import annotations

from abc import ABC, abstractmethod

from order_pagination.domain.entities import Order


class OrderIterator(ABC):
    """The Iterator: traverses a collection of orders one element at a time,

    without exposing how (or in what batches) they are actually fetched.
    """

    @abstractmethod
    def has_next(self) -> bool:
        """Return True if there is at least one more order to traverse."""

    @abstractmethod
    def next(self) -> Order:
        """Return the next order and advance the iterator's position."""


class OrderRepository(ABC):
    """The Aggregate's data-access boundary: fetches orders page by page."""

    @abstractmethod
    def fetch_page(
        self, cursor: str | None, limit: int
    ) -> tuple[list[Order], str | None]:
        """Return up to `limit` orders after `cursor`, and the next cursor (if any)."""
