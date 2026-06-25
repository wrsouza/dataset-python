"""Unit tests for ListProductsPageUseCase and SummarizeByCategoryUseCase."""

from __future__ import annotations

from catalog_iterator.application.use_cases import (
    ListProductsPageUseCase,
    SummarizeByCategoryUseCase,
)
from catalog_iterator.domain.entities import Product
from catalog_iterator.domain.interfaces import ProductRepository


class FakeMultiCategoryRepository(ProductRepository):
    def __init__(self) -> None:
        self._products = [
            Product(1, "p1", 10.0, "books"),
            Product(2, "p2", 20.0, "books"),
            Product(3, "p3", 5.0, "toys"),
        ]

    def fetch_chunk(
        self, cursor: str | None, limit: int
    ) -> tuple[list[Product], str | None]:
        last_id = int(cursor) if cursor is not None else 0
        page = [p for p in self._products if p.product_id > last_id][:limit]
        next_cursor = str(page[-1].product_id) if len(page) == limit else None
        return page, next_cursor


def test_list_products_page_returns_requested_page() -> None:
    repository = FakeMultiCategoryRepository()
    use_case = ListProductsPageUseCase(repository)

    page = use_case.execute(cursor=None, limit=2)

    assert [p.product_id for p in page.items] == [1, 2]
    assert page.next_cursor == "2"


def test_summarize_by_category_aggregates_correctly() -> None:
    repository = FakeMultiCategoryRepository()
    use_case = SummarizeByCategoryUseCase(repository, chunk_size=1)

    summaries = use_case.execute()

    by_category = {s.category: s for s in summaries}
    assert by_category["books"].product_count == 2
    assert by_category["books"].total_price == 30.0
    assert by_category["toys"].product_count == 1
    assert by_category["toys"].total_price == 5.0


def test_summarize_empty_catalog_returns_empty_list() -> None:
    class EmptyRepository(ProductRepository):
        def fetch_chunk(
            self, cursor: str | None, limit: int
        ) -> tuple[list[Product], str | None]:
            return [], None

    summaries = SummarizeByCategoryUseCase(EmptyRepository()).execute()

    assert summaries == []
