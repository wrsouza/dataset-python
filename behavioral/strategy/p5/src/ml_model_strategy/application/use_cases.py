"""Application use cases for the ML Model Strategy demo."""

from __future__ import annotations

from dataclasses import dataclass

from ml_model_strategy.application.context import ModelPredictor
from ml_model_strategy.domain.entities import PredictionResult
from ml_model_strategy.infrastructure.strategies.registry import get_strategy


@dataclass
class PredictInput:
    model_name: str
    features: list[float]


class PredictUseCase:
    def execute(self, data: PredictInput) -> PredictionResult:
        strategy = get_strategy(data.model_name)
        predictor = ModelPredictor(strategy)
        return predictor.predict(data.features)
