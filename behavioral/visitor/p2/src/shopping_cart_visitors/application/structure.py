"""Cart traversal helper — applies a visitor to every item via accept()."""

from __future__ import annotations

from shopping_cart_visitors.domain.interfaces import (
    CartItem,
    CartVisitor,
    VisitorResult,
)


def traverse(items: list[CartItem], visitor: CartVisitor) -> VisitorResult:
    """Visit every item in the cart and return the visitor's accumulated result."""
    for item in items:
        item.accept(visitor)
    return visitor.result
