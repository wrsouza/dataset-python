"""In-memory implementation of DashboardMediator, scoped to one dashboard session."""

from __future__ import annotations

from dashboard_mediator.domain.entities import FilterCriteria, Product
from dashboard_mediator.domain.interfaces import DashboardMediator


class InMemoryDashboardMediator(DashboardMediator):
    """Holds the product dataset and the shared filter for one dashboard session."""

    def __init__(self, products: list[Product]) -> None:
        self._products = products
        self._filter = FilterCriteria()

    def set_filter(self, criteria: FilterCriteria) -> None:
        self._filter = criteria

    def get_filter(self) -> FilterCriteria:
        return self._filter

    def get_filtered_products(self) -> list[Product]:
        return [p for p in self._products if self._filter.matches(p)]

    def get_categories(self) -> list[str]:
        return sorted({p.category for p in self._products})
