"""ShippingCalculatorVisitor: only physical items ever cost shipping."""

from __future__ import annotations

from shopping_cart_visitors.domain.interfaces import (
    CartVisitor,
    DigitalItem,
    PhysicalItem,
    SubscriptionItem,
    VisitorResult,
)

_COST_PER_KG = 2.5


class ShippingCalculatorVisitor(CartVisitor):
    """Computes shipping cost from each physical item's weight; digital and
    subscription items never ship."""

    def __init__(self) -> None:
        self._total_weight_kg = 0.0

    def visit_physical(self, item: PhysicalItem) -> None:
        self._total_weight_kg += item.weight_kg * item.quantity

    def visit_digital(self, item: DigitalItem) -> None:
        pass

    def visit_subscription(self, item: SubscriptionItem) -> None:
        pass

    @property
    def result(self) -> VisitorResult:
        cost = round(self._total_weight_kg * _COST_PER_KG, 2)
        return VisitorResult(
            data={"total_weight_kg": round(self._total_weight_kg, 2), "cost": cost}
        )
