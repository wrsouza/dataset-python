"""Unit tests for the strategy registry."""

from __future__ import annotations

import pytest

from ml_model_strategy.domain.exceptions import InvalidStrategyError
from ml_model_strategy.infrastructure.strategies.linear_regression import (
    LinearRegressionStrategy,
)
from ml_model_strategy.infrastructure.strategies.registry import (
    get_strategy,
    list_strategy_names,
)


def test_get_strategy_resolves_linear_regression() -> None:
    strategy = get_strategy("linear_regression")

    assert isinstance(strategy, LinearRegressionStrategy)


def test_get_strategy_is_case_insensitive() -> None:
    strategy = get_strategy("DECISION_TREE")

    assert strategy.get_name() == "decision_tree"


def test_get_strategy_raises_for_unknown_name() -> None:
    with pytest.raises(InvalidStrategyError):
        get_strategy("unknown")


def test_list_strategy_names_includes_all_registered() -> None:
    assert list_strategy_names() == [
        "decision_tree",
        "linear_regression",
        "random_forest",
    ]
