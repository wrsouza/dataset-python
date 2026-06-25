"""Unit tests for LazyProductIterator, the concrete GoF Iterator."""

from __future__ import annotations

import pytest

from catalog_iterator.domain.entities import Product
from catalog_iterator.domain.interfaces import ProductRepository
from catalog_iterator.infrastructure.iterator import LazyProductIterator


class FakeProductRepository(ProductRepository):
    """An in-memory ProductRepository that paginates a fixed list of products."""

    def __init__(self, total: int) -> None:
        self._products = [
            Product(product_id=i, name=f"p-{i}", price=float(i), category="general")
            for i in range(1, total + 1)
        ]
        self.fetch_calls = 0

    def fetch_chunk(
        self, cursor: str | None, limit: int
    ) -> tuple[list[Product], str | None]:
        self.fetch_calls += 1
        last_id = int(cursor) if cursor is not None else 0
        page = [p for p in self._products if p.product_id > last_id][:limit]
        next_cursor = str(page[-1].product_id) if len(page) == limit else None
        return page, next_cursor


def test_iterates_every_product_exactly_once() -> None:
    repository = FakeProductRepository(total=7)
    iterator = LazyProductIterator(repository, chunk_size=3)

    seen = []
    while iterator.has_next():
        seen.append(iterator.next().product_id)

    assert seen == [1, 2, 3, 4, 5, 6, 7]


def test_fetches_chunks_lazily_not_all_at_once() -> None:
    repository = FakeProductRepository(total=10)
    iterator = LazyProductIterator(repository, chunk_size=4)

    iterator.next()

    assert repository.fetch_calls == 1


def test_has_next_is_false_for_empty_catalog() -> None:
    repository = FakeProductRepository(total=0)
    iterator = LazyProductIterator(repository, chunk_size=10)

    assert iterator.has_next() is False


def test_next_raises_stop_iteration_when_exhausted() -> None:
    repository = FakeProductRepository(total=1)
    iterator = LazyProductIterator(repository, chunk_size=10)
    iterator.next()

    with pytest.raises(StopIteration):
        iterator.next()
