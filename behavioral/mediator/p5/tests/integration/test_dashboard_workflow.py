"""Integration test: full filter -> widgets workflow with the sample dataset."""

from __future__ import annotations

from dashboard_mediator.application.use_cases import (
    GetDashboardDataUseCase,
    UpdateFilterUseCase,
)
from dashboard_mediator.infrastructure.in_memory_mediator import (
    InMemoryDashboardMediator,
)
from dashboard_mediator.infrastructure.sample_data import SAMPLE_PRODUCTS


def test_filtering_by_category_keeps_widgets_in_sync() -> None:
    mediator = InMemoryDashboardMediator(SAMPLE_PRODUCTS)

    UpdateFilterUseCase(mediator).execute(category="books", max_price=None)
    data = GetDashboardDataUseCase(mediator).execute()

    assert all(p.category == "books" for p in data.products)
    assert len(data.products) == 2


def test_filtering_by_max_price_excludes_expensive_products() -> None:
    mediator = InMemoryDashboardMediator(SAMPLE_PRODUCTS)

    UpdateFilterUseCase(mediator).execute(category=None, max_price=50.0)
    data = GetDashboardDataUseCase(mediator).execute()

    assert all(p.price <= 50.0 for p in data.products)
    assert "Laptop" not in [p.name for p in data.products]


def test_clearing_filter_returns_full_catalog() -> None:
    mediator = InMemoryDashboardMediator(SAMPLE_PRODUCTS)
    UpdateFilterUseCase(mediator).execute(category="books", max_price=None)

    UpdateFilterUseCase(mediator).execute(category=None, max_price=None)
    data = GetDashboardDataUseCase(mediator).execute()

    assert len(data.products) == len(SAMPLE_PRODUCTS)
