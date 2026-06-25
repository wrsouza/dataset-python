"""Unit tests for PercentageDiscountStrategy."""

from __future__ import annotations

import pytest

from discount_strategy_api.infrastructure.strategies.percentage import (
    PercentageDiscountStrategy,
)


def test_apply_discounts_percentage_of_total() -> None:
    strategy = PercentageDiscountStrategy(percentage=10)

    result = strategy.apply(original_total=100.0, quantity=1)

    assert result.discount_amount == 10.0
    assert result.final_total == 90.0
    assert result.strategy_name == "percentage"


def test_rejects_percentage_outside_0_100() -> None:
    with pytest.raises(ValueError, match="percentage"):
        PercentageDiscountStrategy(percentage=150)


def test_get_description_mentions_percentage() -> None:
    strategy = PercentageDiscountStrategy(percentage=25)

    assert "25%" in strategy.get_description()
