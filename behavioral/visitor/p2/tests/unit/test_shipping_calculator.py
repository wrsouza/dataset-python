"""Unit tests for ShippingCalculatorVisitor."""

from __future__ import annotations

from shopping_cart_visitors.application.structure import traverse
from shopping_cart_visitors.domain.interfaces import (
    DigitalItem,
    PhysicalItem,
    SubscriptionItem,
)
from shopping_cart_visitors.infrastructure.visitors.shipping_calculator import (
    ShippingCalculatorVisitor,
)


def test_physical_item_contributes_weight_and_cost() -> None:
    items = [PhysicalItem(name="Book", unit_price=10.0, quantity=2, weight_kg=1.0)]

    result = traverse(items, ShippingCalculatorVisitor())

    assert result.data == {"total_weight_kg": 2.0, "cost": 5.0}


def test_digital_and_subscription_items_never_ship() -> None:
    items = [
        DigitalItem(name="E-book", unit_price=10.0, quantity=5),
        SubscriptionItem(
            name="Pro Plan", unit_price=10.0, quantity=1, billing_period="monthly"
        ),
    ]

    result = traverse(items, ShippingCalculatorVisitor())

    assert result.data == {"total_weight_kg": 0.0, "cost": 0.0}
