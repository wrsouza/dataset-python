"""Unit tests for USFederalTaxStrategy: federal rate + state rate."""

from __future__ import annotations

from decimal import Decimal

from tax.domain.entities import Customer, Order
from tax.infrastructure.strategies.us_federal import USFederalTaxStrategy


def test_calculate_applies_federal_and_state_tax(
    order: Order, us_customer: Customer
) -> None:
    strategy = USFederalTaxStrategy(state_code="CA")

    breakdown = strategy.calculate(order, us_customer)

    names = {line.name for line in breakdown.taxes}
    assert names == {"US Federal Tax", "State Tax (CA)"}


def test_calculate_unknown_state_falls_back_to_default(
    order: Order, us_customer: Customer
) -> None:
    strategy = USFederalTaxStrategy(state_code="ZZ")

    breakdown = strategy.calculate(order, us_customer)

    state_line = next(t for t in breakdown.taxes if t.name.startswith("State Tax"))
    assert state_line.rate == Decimal("0.05")


def test_calculate_returns_correct_total(order: Order, us_customer: Customer) -> None:
    strategy = USFederalTaxStrategy(state_code="TX")

    breakdown = strategy.calculate(order, us_customer)

    expected_tax = order.subtotal * (Decimal("0.10") + Decimal("0.0625"))
    assert breakdown.total == order.subtotal + expected_tax


def test_get_name_returns_us() -> None:
    assert USFederalTaxStrategy().get_name() == "us"


def test_state_code_is_normalized_to_uppercase(
    order: Order, us_customer: Customer
) -> None:
    strategy = USFederalTaxStrategy(state_code="ny")

    breakdown = strategy.calculate(order, us_customer)

    assert any("NY" in t.name for t in breakdown.taxes)
