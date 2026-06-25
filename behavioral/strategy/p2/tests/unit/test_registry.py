"""Unit tests for the strategy registry."""

from __future__ import annotations

import pytest

from discount_strategy_api.domain.exceptions import InvalidStrategyError
from discount_strategy_api.infrastructure.strategies.bulk_quantity import (
    BulkQuantityDiscountStrategy,
)
from discount_strategy_api.infrastructure.strategies.percentage import (
    PercentageDiscountStrategy,
)
from discount_strategy_api.infrastructure.strategies.registry import (
    get_strategy,
    list_strategy_names,
)


def test_get_strategy_builds_percentage_strategy() -> None:
    strategy = get_strategy("percentage", {"percentage": 10})

    assert isinstance(strategy, PercentageDiscountStrategy)


def test_get_strategy_builds_bulk_quantity_strategy() -> None:
    strategy = get_strategy("bulk_quantity", {"threshold": 5, "percentage": 15})

    assert isinstance(strategy, BulkQuantityDiscountStrategy)


def test_get_strategy_is_case_insensitive() -> None:
    strategy = get_strategy("NO_DISCOUNT")

    assert strategy.get_name() == "no_discount"


def test_get_strategy_raises_for_unknown_name() -> None:
    with pytest.raises(InvalidStrategyError):
        get_strategy("unknown")


def test_list_strategy_names_includes_all_registered() -> None:
    names = list_strategy_names()

    assert "percentage" in names
    assert "fixed_amount" in names
    assert "bulk_quantity" in names
    assert "no_discount" in names
