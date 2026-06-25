"""RandomForestStrategy — averages three deterministic decision-tree-like
rules, standing in for a trained ensemble; confidence reflects how much
the "trees" agree with each other."""

from __future__ import annotations

import statistics

from ml_model_strategy.domain.entities import PredictionResult
from ml_model_strategy.domain.exceptions import FeatureMismatchError
from ml_model_strategy.domain.interfaces import MLModelStrategy


def _tree_a(size: float, age: float, location_score: float) -> float:
    base = 250_000.0 if size >= 100 else 160_000.0
    return base + location_score * 5_000 - age * 1_000


def _tree_b(size: float, age: float, location_score: float) -> float:
    base = 280_000.0 if size >= 80 else 150_000.0
    return base + location_score * 4_000 - age * 1_500


def _tree_c(size: float, age: float, location_score: float) -> float:
    base = 260_000.0 if location_score >= 5 else 170_000.0
    return base + size * 800 - age * 1_200


class RandomForestStrategy(MLModelStrategy):
    def predict(self, features: list[float]) -> PredictionResult:
        if len(features) != self.get_feature_count():
            raise FeatureMismatchError(self.get_feature_count(), len(features))

        size, age, location_score = features
        votes = [
            _tree_a(size, age, location_score),
            _tree_b(size, age, location_score),
            _tree_c(size, age, location_score),
        ]
        prediction = statistics.mean(votes)

        spread = max(votes) - min(votes)
        confidence = (
            max(0.5, 1.0 - min(spread / prediction, 0.5)) if prediction else 0.5
        )

        return PredictionResult(
            model_name=self.get_name(), prediction=prediction, confidence=confidence
        )

    def get_name(self) -> str:
        return "random_forest"

    def get_feature_count(self) -> int:
        return 3
