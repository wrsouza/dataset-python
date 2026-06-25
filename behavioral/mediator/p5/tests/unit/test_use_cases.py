"""Unit tests for UpdateFilterUseCase and GetDashboardDataUseCase."""

from __future__ import annotations

from dashboard_mediator.application.use_cases import (
    GetDashboardDataUseCase,
    UpdateFilterUseCase,
)
from dashboard_mediator.domain.entities import Product
from dashboard_mediator.infrastructure.in_memory_mediator import (
    InMemoryDashboardMediator,
)

PRODUCTS = [
    Product(name="Laptop", category="electronics", price=1200.0),
    Product(name="Novel", category="books", price=18.0),
]


def test_update_filter_use_case_changes_filtered_products() -> None:
    mediator = InMemoryDashboardMediator(PRODUCTS)
    UpdateFilterUseCase(mediator).execute(category="books", max_price=None)

    data = GetDashboardDataUseCase(mediator).execute()

    assert [p.name for p in data.products] == ["Novel"]
    assert data.filter_criteria.category == "books"


def test_get_dashboard_data_includes_categories() -> None:
    mediator = InMemoryDashboardMediator(PRODUCTS)

    data = GetDashboardDataUseCase(mediator).execute()

    assert data.categories == ["books", "electronics"]
