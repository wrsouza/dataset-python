"""Unit tests for InMemoryDashboardMediator."""

from __future__ import annotations

from dashboard_mediator.domain.entities import FilterCriteria, Product
from dashboard_mediator.infrastructure.in_memory_mediator import (
    InMemoryDashboardMediator,
)

PRODUCTS = [
    Product(name="Laptop", category="electronics", price=1200.0),
    Product(name="Headphones", category="electronics", price=150.0),
    Product(name="Novel", category="books", price=18.0),
]


def test_get_filtered_products_returns_everything_by_default() -> None:
    mediator = InMemoryDashboardMediator(PRODUCTS)

    assert len(mediator.get_filtered_products()) == 3


def test_set_filter_by_category() -> None:
    mediator = InMemoryDashboardMediator(PRODUCTS)

    mediator.set_filter(FilterCriteria(category="books"))

    assert [p.name for p in mediator.get_filtered_products()] == ["Novel"]


def test_set_filter_by_max_price() -> None:
    mediator = InMemoryDashboardMediator(PRODUCTS)

    mediator.set_filter(FilterCriteria(max_price=200.0))

    names = {p.name for p in mediator.get_filtered_products()}
    assert names == {"Headphones", "Novel"}


def test_set_filter_combines_category_and_price() -> None:
    mediator = InMemoryDashboardMediator(PRODUCTS)

    mediator.set_filter(FilterCriteria(category="electronics", max_price=200.0))

    assert [p.name for p in mediator.get_filtered_products()] == ["Headphones"]


def test_get_filter_returns_last_set_criteria() -> None:
    mediator = InMemoryDashboardMediator(PRODUCTS)
    criteria = FilterCriteria(category="books")

    mediator.set_filter(criteria)

    assert mediator.get_filter() == criteria


def test_get_categories_returns_sorted_unique_categories() -> None:
    mediator = InMemoryDashboardMediator(PRODUCTS)

    assert mediator.get_categories() == ["books", "electronics"]
