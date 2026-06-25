"""Unit tests for InvoiceFormatterVisitor."""

from __future__ import annotations

from shopping_cart_visitors.application.structure import traverse
from shopping_cart_visitors.domain.interfaces import (
    DigitalItem,
    PhysicalItem,
    SubscriptionItem,
)
from shopping_cart_visitors.infrastructure.visitors.invoice_formatter import (
    InvoiceFormatterVisitor,
)


def test_formats_one_line_per_item_type() -> None:
    items = [
        PhysicalItem(name="Book", unit_price=10.0, quantity=1, weight_kg=0.5),
        DigitalItem(name="E-book", unit_price=5.0, quantity=2),
        SubscriptionItem(
            name="Pro Plan", unit_price=10.0, quantity=1, billing_period="monthly"
        ),
    ]

    result = traverse(items, InvoiceFormatterVisitor())

    lines = result.data["lines"]
    assert "1x Book @ $10.00 (0.50kg each)" in lines
    assert "2x E-book @ $5.00 (digital download)" in lines
    assert "1x Pro Plan @ $10.00/monthly" in lines
