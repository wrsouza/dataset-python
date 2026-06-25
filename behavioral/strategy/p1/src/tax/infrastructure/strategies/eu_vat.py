"""EU VAT strategy: VAT rate per country."""

from __future__ import annotations

from decimal import Decimal

from tax.domain.entities import (
    Customer,
    CustomerCountry,
    Order,
    TaxBreakdown,
    TaxLine,
)
from tax.domain.interfaces import TaxStrategy

# Standard VAT rates per EU country (2024)
_EU_VAT_RATES: dict[CustomerCountry, Decimal] = {
    CustomerCountry.GERMANY: Decimal("0.19"),
    CustomerCountry.FRANCE: Decimal("0.20"),
    CustomerCountry.PORTUGAL: Decimal("0.23"),
    CustomerCountry.ITALY: Decimal("0.22"),
    CustomerCountry.SPAIN: Decimal("0.21"),
    CustomerCountry.NETHERLANDS: Decimal("0.21"),
}

_DEFAULT_EU_VAT = Decimal("0.20")


class EUVATStrategy(TaxStrategy):
    """Applies EU Value Added Tax based on customer country."""

    def calculate(self, order: Order, customer: Customer) -> TaxBreakdown:
        subtotal = order.subtotal
        vat_rate = _EU_VAT_RATES.get(customer.country, _DEFAULT_EU_VAT)
        vat_amount = subtotal * vat_rate

        taxes = [
            TaxLine(
                name=f"VAT ({customer.country.value})",
                rate=vat_rate,
                amount=vat_amount,
                description=f"Value Added Tax — {customer.country.value} standard rate",
            ),
        ]
        total = subtotal + vat_amount
        effective_rate = vat_amount / subtotal if subtotal else Decimal("0")

        return TaxBreakdown(
            subtotal=subtotal,
            taxes=taxes,
            total=total,
            effective_rate=effective_rate,
            strategy_used=self.get_name(),
        )

    def get_name(self) -> str:
        return "eu"

    def get_description(self) -> str:
        return "EU VAT per country (DE 19%, FR 20%, PT 23%, IT 22%, ES/NL 21%)"
