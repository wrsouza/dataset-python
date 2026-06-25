"""InvoiceFormatterVisitor: renders one human-readable line per item."""

from __future__ import annotations

from shopping_cart_visitors.domain.interfaces import (
    CartVisitor,
    DigitalItem,
    PhysicalItem,
    SubscriptionItem,
    VisitorResult,
)


class InvoiceFormatterVisitor(CartVisitor):
    """Builds an invoice line for each item, formatted per its own type."""

    def __init__(self) -> None:
        self._lines: list[str] = []

    def visit_physical(self, item: PhysicalItem) -> None:
        self._lines.append(
            f"{item.quantity}x {item.name} @ ${item.unit_price:.2f} "
            f"({item.weight_kg:.2f}kg each)"
        )

    def visit_digital(self, item: DigitalItem) -> None:
        self._lines.append(
            f"{item.quantity}x {item.name} @ ${item.unit_price:.2f} (digital download)"
        )

    def visit_subscription(self, item: SubscriptionItem) -> None:
        self._lines.append(
            f"{item.quantity}x {item.name} @ ${item.unit_price:.2f}/"
            f"{item.billing_period}"
        )

    @property
    def result(self) -> VisitorResult:
        return VisitorResult(data={"lines": list(self._lines)})
