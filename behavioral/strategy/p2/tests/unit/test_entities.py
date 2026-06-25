"""Unit tests for the DiscountResult domain entity."""

from __future__ import annotations

import pytest

from discount_strategy_api.domain.entities import DiscountResult


def test_rejects_negative_original_total() -> None:
    with pytest.raises(ValueError, match="original_total"):
        DiscountResult(
            original_total=-1.0,
            discount_amount=0.0,
            final_total=-1.0,
            strategy_name="x",
        )


def test_rejects_negative_discount_amount() -> None:
    with pytest.raises(ValueError, match="discount_amount"):
        DiscountResult(
            original_total=10.0,
            discount_amount=-1.0,
            final_total=11.0,
            strategy_name="x",
        )
