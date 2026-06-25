"""Abstraction for the Mediator pattern between dashboard widgets."""

from __future__ import annotations

from abc import ABC, abstractmethod

from dashboard_mediator.domain.entities import FilterCriteria, Product


class DashboardMediator(ABC):
    """The Mediator: holds the shared filter state and the filtered dataset.

    Widgets (the filter panel, the chart, the table) never reference one
    another — each only ever reads or writes through this mediator.
    """

    @abstractmethod
    def set_filter(self, criteria: FilterCriteria) -> None:
        """Update the shared filter criteria."""

    @abstractmethod
    def get_filter(self) -> FilterCriteria:
        """Return the current filter criteria."""

    @abstractmethod
    def get_filtered_products(self) -> list[Product]:
        """Return every product that matches the current filter criteria."""

    @abstractmethod
    def get_categories(self) -> list[str]:
        """Return every distinct category in the underlying dataset."""
