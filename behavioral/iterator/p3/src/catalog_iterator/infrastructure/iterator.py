"""Concrete Iterator: lazily walks every product, fetching chunks on demand."""

from __future__ import annotations

from collections import deque

from catalog_iterator.domain.entities import Product
from catalog_iterator.domain.interfaces import ProductIterator, ProductRepository


class LazyProductIterator(ProductIterator):
    """Traverses every product in the catalog one at a time.

    Internally fetches batches of `chunk_size` products from the
    repository as the buffer empties — the client only ever sees
    `has_next`/`next`, never the underlying keyset queries.
    """

    def __init__(self, repository: ProductRepository, chunk_size: int = 500) -> None:
        self._repository = repository
        self._chunk_size = chunk_size
        self._buffer: deque[Product] = deque()
        self._cursor: str | None = None
        self._exhausted = False

    def has_next(self) -> bool:
        if not self._buffer and not self._exhausted:
            self._load_next_chunk()
        return bool(self._buffer)

    def next(self) -> Product:
        if not self.has_next():
            raise StopIteration("No more products to iterate")
        return self._buffer.popleft()

    def _load_next_chunk(self) -> None:
        items, next_cursor = self._repository.fetch_chunk(
            self._cursor, self._chunk_size
        )
        self._buffer.extend(items)
        self._cursor = next_cursor
        if next_cursor is None:
            self._exhausted = True
