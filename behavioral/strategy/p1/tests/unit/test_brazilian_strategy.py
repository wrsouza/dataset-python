"""Unit tests for BrazilianTaxStrategy: ICMS + PIS + COFINS."""

from __future__ import annotations

from decimal import Decimal

from tax.domain.entities import Customer, Order
from tax.infrastructure.strategies.brazilian import BrazilianTaxStrategy


def test_calculate_applies_icms_pis_and_cofins(
    order: Order, brazilian_customer: Customer
) -> None:
    strategy = BrazilianTaxStrategy()

    breakdown = strategy.calculate(order, brazilian_customer)

    names = {line.name for line in breakdown.taxes}
    assert names == {"ICMS", "PIS", "COFINS"}


def test_calculate_returns_correct_total(
    order: Order, brazilian_customer: Customer
) -> None:
    strategy = BrazilianTaxStrategy()

    breakdown = strategy.calculate(order, brazilian_customer)

    expected_tax = order.subtotal * Decimal("0.2165")
    assert breakdown.total == order.subtotal + expected_tax
    assert breakdown.subtotal == order.subtotal


def test_calculate_sets_strategy_used(
    order: Order, brazilian_customer: Customer
) -> None:
    strategy = BrazilianTaxStrategy()

    breakdown = strategy.calculate(order, brazilian_customer)

    assert breakdown.strategy_used == "brazil"


def test_get_name_returns_brazil() -> None:
    assert BrazilianTaxStrategy().get_name() == "brazil"


def test_get_description_mentions_tax_names() -> None:
    description = BrazilianTaxStrategy().get_description()

    assert "ICMS" in description
    assert "PIS" in description
    assert "COFINS" in description
