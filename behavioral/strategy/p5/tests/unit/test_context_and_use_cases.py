"""Unit tests for the ModelPredictor context and PredictUseCase."""

from __future__ import annotations

import pytest

from ml_model_strategy.application.context import (
    ModelPredictor,
    NoStrategyConfiguredError,
)
from ml_model_strategy.application.use_cases import PredictInput, PredictUseCase
from ml_model_strategy.domain.exceptions import InvalidStrategyError
from ml_model_strategy.infrastructure.strategies.decision_tree import (
    DecisionTreeStrategy,
)
from ml_model_strategy.infrastructure.strategies.linear_regression import (
    LinearRegressionStrategy,
)


def test_predict_raises_without_strategy() -> None:
    predictor = ModelPredictor()

    with pytest.raises(NoStrategyConfiguredError):
        predictor.predict([1.0, 2.0, 3.0])


def test_set_strategy_swaps_strategy_at_runtime() -> None:
    predictor = ModelPredictor(LinearRegressionStrategy())

    predictor.set_strategy(DecisionTreeStrategy())
    result = predictor.predict([90.0, 10.0, 6.0])

    assert result.model_name == "decision_tree"
    assert predictor.current_strategy is not None
    assert predictor.current_strategy.get_name() == "decision_tree"


def test_predict_use_case_delegates_to_registry_and_context() -> None:
    use_case = PredictUseCase()

    result = use_case.execute(
        PredictInput(model_name="linear_regression", features=[90.0, 10.0, 6.0])
    )

    assert result.model_name == "linear_regression"


def test_predict_use_case_raises_for_unknown_model() -> None:
    use_case = PredictUseCase()

    with pytest.raises(InvalidStrategyError):
        use_case.execute(PredictInput(model_name="unknown", features=[1.0]))
