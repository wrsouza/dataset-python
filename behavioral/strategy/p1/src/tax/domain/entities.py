"""Domain entities and value objects for the tax calculation domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum


class OrderType(StrEnum):
    """Commercial classification of an order."""

    B2B = "B2B"
    B2C = "B2C"
    EXPORT = "EXPORT"


class CustomerCountry(StrEnum):
    """ISO-like country code used to resolve the applicable tax jurisdiction."""

    BRAZIL = "BR"
    USA = "US"
    GERMANY = "DE"
    FRANCE = "FR"
    PORTUGAL = "PT"
    ITALY = "IT"
    SPAIN = "ES"
    NETHERLANDS = "NL"
    OTHER = "OTHER"


@dataclass
class Customer:
    """A buyer placing an order, identified by tax jurisdiction and exemption status."""

    id: str
    name: str
    country: CustomerCountry
    tax_id: str | None = None
    is_exempt: bool = False


@dataclass
class OrderItem:
    """A single line item belonging to an order."""

    product_id: str
    description: str
    quantity: int
    unit_price: Decimal


@dataclass
class Order:
    """A purchase composed of one or more order items."""

    id: str
    customer_id: str
    order_type: OrderType
    items: list[OrderItem] = field(default_factory=list)

    @property
    def subtotal(self) -> Decimal:
        """Sum of quantity * unit_price across all items, before taxes."""
        return sum(
            (item.unit_price * item.quantity for item in self.items),
            start=Decimal("0"),
        )


@dataclass
class TaxLine:
    """A single tax charge applied to an order (e.g. VAT, ICMS, state tax)."""

    name: str
    rate: Decimal
    amount: Decimal
    description: str = ""


@dataclass
class TaxBreakdown:
    """The full result of a tax calculation: every TaxLine plus totals."""

    subtotal: Decimal
    taxes: list[TaxLine]
    total: Decimal
    effective_rate: Decimal
    strategy_used: str = ""

    @classmethod
    def zero(cls, subtotal: Decimal, strategy_name: str) -> TaxBreakdown:
        """Build a breakdown with no taxes applied (e.g. exempt customers)."""
        return cls(
            subtotal=subtotal,
            taxes=[],
            total=subtotal,
            effective_rate=Decimal("0"),
            strategy_used=strategy_name,
        )
