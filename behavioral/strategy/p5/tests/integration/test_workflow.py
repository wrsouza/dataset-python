"""Integration-style test exercising every model strategy through the
same use case, mirroring how the Streamlit app wires the selectbox."""

from __future__ import annotations

from ml_model_strategy.application.use_cases import PredictInput, PredictUseCase
from ml_model_strategy.infrastructure.strategies.registry import list_strategy_names


def test_every_registered_model_produces_a_valid_prediction() -> None:
    use_case = PredictUseCase()

    for model_name in list_strategy_names():
        result = use_case.execute(
            PredictInput(model_name=model_name, features=[90.0, 10.0, 6.0])
        )

        assert result.model_name == model_name
        assert result.prediction > 0
        assert 0.0 <= result.confidence <= 1.0
