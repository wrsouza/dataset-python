"""Unit tests for PriceCalculatorVisitor."""

from __future__ import annotations

from shopping_cart_visitors.application.structure import traverse
from shopping_cart_visitors.domain.interfaces import (
    DigitalItem,
    PhysicalItem,
    SubscriptionItem,
)
from shopping_cart_visitors.infrastructure.visitors.price_calculator import (
    PriceCalculatorVisitor,
)


def test_physical_item_taxed_at_8_percent() -> None:
    items = [PhysicalItem(name="Book", unit_price=100.0, quantity=1, weight_kg=0.5)]

    result = traverse(items, PriceCalculatorVisitor())

    assert result.data == {"subtotal": 100.0, "tax": 8.0, "total": 108.0}


def test_digital_item_taxed_at_5_percent() -> None:
    items = [DigitalItem(name="E-book", unit_price=20.0, quantity=2)]

    result = traverse(items, PriceCalculatorVisitor())

    assert result.data["subtotal"] == 40.0
    assert result.data["tax"] == 2.0


def test_subscription_item_yearly_multiplies_by_12() -> None:
    items = [
        SubscriptionItem(
            name="Pro Plan", unit_price=10.0, quantity=1, billing_period="yearly"
        )
    ]

    result = traverse(items, PriceCalculatorVisitor())

    assert result.data["subtotal"] == 120.0
    assert result.data["tax"] == 0.0


def test_mixed_cart_sums_all_item_types() -> None:
    items = [
        PhysicalItem(name="Book", unit_price=100.0, quantity=1, weight_kg=0.5),
        DigitalItem(name="E-book", unit_price=20.0, quantity=1),
        SubscriptionItem(
            name="Pro Plan", unit_price=10.0, quantity=1, billing_period="monthly"
        ),
    ]

    result = traverse(items, PriceCalculatorVisitor())

    assert result.data["subtotal"] == 130.0
