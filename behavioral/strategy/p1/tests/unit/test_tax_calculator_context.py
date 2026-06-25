"""Unit tests for TaxCalculator context: strategy delegation and runtime swap."""

from __future__ import annotations

import pytest

from tax.application.context import TaxCalculator
from tax.domain.entities import Customer, Order
from tax.domain.exceptions import NoStrategyConfiguredError
from tax.infrastructure.strategies.brazilian import BrazilianTaxStrategy
from tax.infrastructure.strategies.exempt import ExemptTaxStrategy


def test_calculate_raises_when_no_strategy_configured(
    order: Order, brazilian_customer: Customer
) -> None:
    calculator = TaxCalculator()

    with pytest.raises(NoStrategyConfiguredError):
        calculator.calculate(order, brazilian_customer)


def test_calculate_delegates_to_injected_strategy(
    order: Order, brazilian_customer: Customer
) -> None:
    calculator = TaxCalculator(strategy=BrazilianTaxStrategy())

    breakdown = calculator.calculate(order, brazilian_customer)

    assert breakdown.strategy_used == "brazil"


def test_set_strategy_swaps_behavior_at_runtime(
    order: Order, brazilian_customer: Customer
) -> None:
    calculator = TaxCalculator(strategy=BrazilianTaxStrategy())

    calculator.set_strategy(ExemptTaxStrategy())
    breakdown = calculator.calculate(order, brazilian_customer)

    assert breakdown.strategy_used == "exempt"
    assert breakdown.taxes == []


def test_current_strategy_reflects_configured_strategy() -> None:
    strategy = ExemptTaxStrategy()
    calculator = TaxCalculator(strategy=strategy)

    assert calculator.current_strategy is strategy
