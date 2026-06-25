"""PriceCalculatorVisitor: computes the cart's total, with per-type tax rules."""

from __future__ import annotations

from shopping_cart_visitors.domain.interfaces import (
    CartVisitor,
    DigitalItem,
    PhysicalItem,
    SubscriptionItem,
    VisitorResult,
)

_PHYSICAL_TAX_RATE = 0.08
_DIGITAL_TAX_RATE = 0.05
_SUBSCRIPTION_TAX_RATE = 0.0

_PERIOD_MULTIPLIER = {"monthly": 1, "yearly": 12}


class PriceCalculatorVisitor(CartVisitor):
    """Sums each item's subtotal plus its type-specific tax."""

    def __init__(self) -> None:
        self._subtotal = 0.0
        self._tax = 0.0

    def visit_physical(self, item: PhysicalItem) -> None:
        subtotal = item.unit_price * item.quantity
        self._subtotal += subtotal
        self._tax += subtotal * _PHYSICAL_TAX_RATE

    def visit_digital(self, item: DigitalItem) -> None:
        subtotal = item.unit_price * item.quantity
        self._subtotal += subtotal
        self._tax += subtotal * _DIGITAL_TAX_RATE

    def visit_subscription(self, item: SubscriptionItem) -> None:
        multiplier = _PERIOD_MULTIPLIER.get(item.billing_period, 1)
        subtotal = item.unit_price * item.quantity * multiplier
        self._subtotal += subtotal
        self._tax += subtotal * _SUBSCRIPTION_TAX_RATE

    @property
    def result(self) -> VisitorResult:
        return VisitorResult(
            data={
                "subtotal": round(self._subtotal, 2),
                "tax": round(self._tax, 2),
                "total": round(self._subtotal + self._tax, 2),
            }
        )
