"""Unit tests for BulkQuantityDiscountStrategy."""

from __future__ import annotations

import pytest

from discount_strategy_api.infrastructure.strategies.bulk_quantity import (
    BulkQuantityDiscountStrategy,
)


def test_apply_below_threshold_gives_no_discount() -> None:
    strategy = BulkQuantityDiscountStrategy(threshold=10, percentage=20)

    result = strategy.apply(original_total=100.0, quantity=5)

    assert result.discount_amount == 0.0
    assert result.final_total == 100.0


def test_apply_at_threshold_gives_discount() -> None:
    strategy = BulkQuantityDiscountStrategy(threshold=10, percentage=20)

    result = strategy.apply(original_total=100.0, quantity=10)

    assert result.discount_amount == 20.0
    assert result.final_total == 80.0


def test_rejects_threshold_below_one() -> None:
    with pytest.raises(ValueError, match="threshold"):
        BulkQuantityDiscountStrategy(threshold=0, percentage=10)


def test_rejects_percentage_outside_0_100() -> None:
    with pytest.raises(ValueError, match="percentage"):
        BulkQuantityDiscountStrategy(threshold=5, percentage=150)


def test_get_description_mentions_threshold_and_percentage() -> None:
    strategy = BulkQuantityDiscountStrategy(threshold=10, percentage=20)

    description = strategy.get_description()

    assert "10" in description
    assert "20%" in description
