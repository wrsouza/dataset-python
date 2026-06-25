"""Unit tests for ExemptTaxStrategy: zero tax for exempt customers."""

from __future__ import annotations

from decimal import Decimal

from tax.domain.entities import Customer, Order
from tax.infrastructure.strategies.exempt import ExemptTaxStrategy


def test_calculate_returns_zero_taxes(order: Order, exempt_customer: Customer) -> None:
    strategy = ExemptTaxStrategy()

    breakdown = strategy.calculate(order, exempt_customer)

    assert breakdown.taxes == []
    assert breakdown.effective_rate == Decimal("0")


def test_calculate_total_equals_subtotal(
    order: Order, exempt_customer: Customer
) -> None:
    strategy = ExemptTaxStrategy()

    breakdown = strategy.calculate(order, exempt_customer)

    assert breakdown.total == order.subtotal


def test_get_name_returns_exempt() -> None:
    assert ExemptTaxStrategy().get_name() == "exempt"
