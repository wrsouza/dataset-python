"""Unit tests for EUVATStrategy: VAT rate varies per EU country."""

from __future__ import annotations

from decimal import Decimal

from tax.domain.entities import Customer, CustomerCountry, Order
from tax.infrastructure.strategies.eu_vat import EUVATStrategy


def test_calculate_applies_german_vat_rate(
    order: Order, german_customer: Customer
) -> None:
    strategy = EUVATStrategy()

    breakdown = strategy.calculate(order, german_customer)

    assert len(breakdown.taxes) == 1
    assert breakdown.taxes[0].rate == Decimal("0.19")


def test_calculate_falls_back_to_default_rate_for_unmapped_country(
    order: Order,
) -> None:
    strategy = EUVATStrategy()
    customer = Customer(
        id="customer-1",
        name="Unknown EU Customer",
        country=CustomerCountry.OTHER,
    )

    breakdown = strategy.calculate(order, customer)

    assert breakdown.taxes[0].rate == Decimal("0.20")


def test_calculate_returns_correct_total(
    order: Order, german_customer: Customer
) -> None:
    strategy = EUVATStrategy()

    breakdown = strategy.calculate(order, german_customer)

    expected_vat = order.subtotal * Decimal("0.19")
    assert breakdown.total == order.subtotal + expected_vat


def test_get_name_returns_eu() -> None:
    assert EUVATStrategy().get_name() == "eu"
