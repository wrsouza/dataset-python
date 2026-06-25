"""Unit tests for the concrete model strategies."""

from __future__ import annotations

import pytest

from ml_model_strategy.domain.exceptions import FeatureMismatchError
from ml_model_strategy.infrastructure.strategies.decision_tree import (
    DecisionTreeStrategy,
)
from ml_model_strategy.infrastructure.strategies.linear_regression import (
    LinearRegressionStrategy,
)
from ml_model_strategy.infrastructure.strategies.random_forest import (
    RandomForestStrategy,
)

ALL_STRATEGIES = [
    LinearRegressionStrategy(),
    DecisionTreeStrategy(),
    RandomForestStrategy(),
]


@pytest.mark.parametrize("strategy", ALL_STRATEGIES)
def test_predict_returns_result_with_matching_model_name(strategy: object) -> None:
    result = strategy.predict([90.0, 10.0, 6.0])  # type: ignore[attr-defined]

    assert result.model_name == strategy.get_name()  # type: ignore[attr-defined]
    assert 0.0 <= result.confidence <= 1.0


@pytest.mark.parametrize("strategy", ALL_STRATEGIES)
def test_predict_raises_on_feature_count_mismatch(strategy: object) -> None:
    with pytest.raises(FeatureMismatchError):
        strategy.predict([1.0, 2.0])  # type: ignore[attr-defined]


def test_linear_regression_is_deterministic() -> None:
    strategy = LinearRegressionStrategy()

    first = strategy.predict([90.0, 10.0, 6.0])
    second = strategy.predict([90.0, 10.0, 6.0])

    assert first == second


def test_decision_tree_applies_age_discount() -> None:
    strategy = DecisionTreeStrategy()

    new_home = strategy.predict([120.0, 5.0, 8.0])
    old_home = strategy.predict([120.0, 35.0, 8.0])

    assert old_home.prediction < new_home.prediction


def test_random_forest_averages_three_trees() -> None:
    strategy = RandomForestStrategy()

    result = strategy.predict([90.0, 10.0, 6.0])

    assert result.prediction > 0
