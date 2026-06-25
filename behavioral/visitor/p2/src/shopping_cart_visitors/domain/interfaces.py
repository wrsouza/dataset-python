"""Domain interfaces: CartVisitor ABC and CartItem ABC for the Shopping Cart.

Visitor pattern separates the algorithm (pricing, shipping, invoicing)
from the data structure (cart items), enabling new operations without
modifying the item classes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class VisitorResult:
    """Aggregated result returned after a visitor traverses the full cart."""

    data: dict[str, Any] = field(default_factory=dict)


class CartVisitor(ABC):
    """Abstract Visitor — one visit_X method per concrete CartItem type.

    Adding a new operation means creating a new CartVisitor subclass;
    existing CartItem subclasses are never modified (OCP).
    """

    @abstractmethod
    def visit_physical(self, item: PhysicalItem) -> None:
        """Process a physical (shippable) item."""

    @abstractmethod
    def visit_digital(self, item: DigitalItem) -> None:
        """Process a digital (download) item."""

    @abstractmethod
    def visit_subscription(self, item: SubscriptionItem) -> None:
        """Process a recurring subscription item."""

    @property
    def result(self) -> VisitorResult:
        """Return the accumulated result after traversal."""
        return VisitorResult()


class CartItem(ABC):
    """Abstract Element — every cart item exposes accept(visitor).

    Double-dispatch: the item calls the specific visit_X on the visitor,
    so the visitor always knows the concrete type without isinstance checks.
    """

    @abstractmethod
    def accept(self, visitor: CartVisitor) -> None:
        """Accept a visitor and call the appropriate visit_X method."""


@dataclass
class PhysicalItem(CartItem):
    """A shippable item, priced per unit and weighed for shipping."""

    name: str
    unit_price: float
    quantity: int
    weight_kg: float

    def accept(self, visitor: CartVisitor) -> None:
        visitor.visit_physical(self)


@dataclass
class DigitalItem(CartItem):
    """A download, never shipped and taxed differently from physical goods."""

    name: str
    unit_price: float
    quantity: int

    def accept(self, visitor: CartVisitor) -> None:
        visitor.visit_digital(self)


@dataclass
class SubscriptionItem(CartItem):
    """A recurring charge, billed per period rather than per unit."""

    name: str
    unit_price: float
    quantity: int
    billing_period: str  # "monthly" | "yearly"

    def accept(self, visitor: CartVisitor) -> None:
        visitor.visit_subscription(self)


__all__ = [
    "CartVisitor",
    "CartItem",
    "VisitorResult",
    "PhysicalItem",
    "DigitalItem",
    "SubscriptionItem",
]
