"""Use cases orchestrating filter updates and dashboard data retrieval."""

from __future__ import annotations

from dataclasses import dataclass

from dashboard_mediator.domain.entities import FilterCriteria, Product
from dashboard_mediator.domain.interfaces import DashboardMediator


class UpdateFilterUseCase:
    """Updates the shared filter criteria through the mediator."""

    def __init__(self, mediator: DashboardMediator) -> None:
        self._mediator = mediator

    def execute(self, category: str | None, max_price: float | None) -> None:
        self._mediator.set_filter(
            FilterCriteria(category=category, max_price=max_price)
        )


@dataclass(frozen=True)
class DashboardData:
    """Everything a widget needs to render: the filter and the matching products."""

    filter_criteria: FilterCriteria
    products: list[Product]
    categories: list[str]


class GetDashboardDataUseCase:
    """Reads the current filter and the resulting filtered dataset."""

    def __init__(self, mediator: DashboardMediator) -> None:
        self._mediator = mediator

    def execute(self) -> DashboardData:
        return DashboardData(
            filter_criteria=self._mediator.get_filter(),
            products=self._mediator.get_filtered_products(),
            categories=self._mediator.get_categories(),
        )
