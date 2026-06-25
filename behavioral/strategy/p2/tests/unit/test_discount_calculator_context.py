"""Unit tests for the DiscountCalculator context."""

from __future__ import annotations

import pytest

from discount_strategy_api.application.context import DiscountCalculator
from discount_strategy_api.domain.exceptions import NoStrategyConfiguredError
from discount_strategy_api.infrastructure.strategies.no_discount import (
    NoDiscountStrategy,
)
from discount_strategy_api.infrastructure.strategies.percentage import (
    PercentageDiscountStrategy,
)


def test_calculate_raises_without_strategy() -> None:
    calculator = DiscountCalculator()

    with pytest.raises(NoStrategyConfiguredError):
        calculator.calculate(100.0, 1)


def test_calculate_delegates_to_configured_strategy() -> None:
    calculator = DiscountCalculator(PercentageDiscountStrategy(percentage=10))

    result = calculator.calculate(100.0, 1)

    assert result.discount_amount == 10.0


def test_set_strategy_swaps_strategy_at_runtime() -> None:
    calculator = DiscountCalculator(PercentageDiscountStrategy(percentage=10))

    calculator.set_strategy(NoDiscountStrategy())
    result = calculator.calculate(100.0, 1)

    assert result.discount_amount == 0.0
    assert calculator.current_strategy is not None
    assert calculator.current_strategy.get_name() == "no_discount"
