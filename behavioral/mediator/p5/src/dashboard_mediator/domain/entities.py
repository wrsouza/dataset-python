"""Core entities for the dashboard component mediator domain."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    """A single catalog item shown across dashboard widgets."""

    name: str
    category: str
    price: float


@dataclass(frozen=True)
class FilterCriteria:
    """The shared filter state every widget reads through the mediator."""

    category: str | None = None
    max_price: float | None = None

    def matches(self, product: Product) -> bool:
        if self.category is not None and product.category != self.category:
            return False
        if self.max_price is not None and product.price > self.max_price:
            return False
        return True
