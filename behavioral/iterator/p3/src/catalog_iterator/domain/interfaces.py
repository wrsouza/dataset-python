"""Abstractions for the Iterator pattern and the underlying Django queryset access."""

from __future__ import annotations

from abc import ABC, abstractmethod

from catalog_iterator.domain.entities import Product


class ProductIterator(ABC):
    """The Iterator: traverses every product in the catalog one at a time,

    without exposing how (or in what chunks) the queryset was fetched.
    """

    @abstractmethod
    def has_next(self) -> bool:
        """Return True if there is at least one more product to traverse."""

    @abstractmethod
    def next(self) -> Product:
        """Return the next product and advance the iterator's position."""


class ProductRepository(ABC):
    """The Aggregate's data-access boundary: fetches products chunk by chunk."""

    @abstractmethod
    def fetch_chunk(
        self, cursor: str | None, limit: int
    ) -> tuple[list[Product], str | None]:
        """Return up to `limit` products after `cursor`, and the next cursor."""
