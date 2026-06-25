"""Unit tests for NoDiscountStrategy."""

from __future__ import annotations

from discount_strategy_api.infrastructure.strategies.no_discount import (
    NoDiscountStrategy,
)


def test_apply_leaves_total_unchanged() -> None:
    strategy = NoDiscountStrategy()

    result = strategy.apply(original_total=100.0, quantity=1)

    assert result.discount_amount == 0.0
    assert result.final_total == 100.0
    assert result.strategy_name == "no_discount"


def test_get_description() -> None:
    strategy = NoDiscountStrategy()

    assert strategy.get_description() == "No discount applied"
