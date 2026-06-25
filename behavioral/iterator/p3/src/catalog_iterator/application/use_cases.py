"""Use cases orchestrating paginated listing and full-catalog aggregation."""

from __future__ import annotations

from collections import defaultdict

from catalog_iterator.domain.entities import CategorySummary, Product, ProductsPage
from catalog_iterator.domain.interfaces import ProductRepository
from catalog_iterator.infrastructure.iterator import LazyProductIterator


class ListProductsPageUseCase:
    """Returns a single page of products — the typical REST pagination request."""

    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self, cursor: str | None, limit: int) -> ProductsPage:
        items, next_cursor = self._repository.fetch_chunk(cursor, limit)
        return ProductsPage(items=items, next_cursor=next_cursor)


class SummarizeByCategoryUseCase:
    """Aggregates count and total price per category by iterating the catalog.

    Demonstrates the GoF Iterator directly: regardless of how many rows
    the catalog has, only one chunk is ever held in memory at a time.
    """

    def __init__(self, repository: ProductRepository, chunk_size: int = 500) -> None:
        self._repository = repository
        self._chunk_size = chunk_size

    def execute(self) -> list[CategorySummary]:
        iterator = LazyProductIterator(self._repository, self._chunk_size)
        counts: dict[str, int] = defaultdict(int)
        totals: dict[str, float] = defaultdict(float)

        while iterator.has_next():
            product: Product = iterator.next()
            counts[product.category] += 1
            totals[product.category] += product.price

        return [
            CategorySummary(
                category=category,
                product_count=counts[category],
                total_price=totals[category],
            )
            for category in sorted(counts)
        ]
