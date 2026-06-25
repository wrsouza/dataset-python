"""Domain entities and value objects for the Shopping Cart context."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class OperationType(StrEnum):
    """The set of operations a client may request over a cart.

    Adding a new ConcreteVisitor (infrastructure/) means adding a new
    member here and wiring it in the use case factory — the cart item
    classes themselves stay untouched (OCP).
    """

    PRICE = "price"
    SHIPPING = "shipping"
    INVOICE = "invoice"


@dataclass(frozen=True)
class CartReport:
    """Outcome of running one operation over a cart's items."""

    operation: OperationType
    data: dict[str, object]
