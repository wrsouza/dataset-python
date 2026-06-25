"""Unit tests for FixedAmountDiscountStrategy."""

from __future__ import annotations

import pytest

from discount_strategy_api.infrastructure.strategies.fixed_amount import (
    FixedAmountDiscountStrategy,
)


def test_apply_subtracts_fixed_amount() -> None:
    strategy = FixedAmountDiscountStrategy(amount=15.0)

    result = strategy.apply(original_total=100.0, quantity=1)

    assert result.discount_amount == 15.0
    assert result.final_total == 85.0


def test_apply_never_discounts_more_than_the_total() -> None:
    strategy = FixedAmountDiscountStrategy(amount=150.0)

    result = strategy.apply(original_total=100.0, quantity=1)

    assert result.discount_amount == 100.0
    assert result.final_total == 0.0


def test_rejects_negative_amount() -> None:
    with pytest.raises(ValueError, match="amount"):
        FixedAmountDiscountStrategy(amount=-5)


def test_get_description_mentions_amount() -> None:
    strategy = FixedAmountDiscountStrategy(amount=15.0)

    assert "15.00" in strategy.get_description()
