"""DecisionTreeStrategy — a small hand-coded rule tree, standing in for a
trained decision tree."""

from __future__ import annotations

from ml_model_strategy.domain.entities import PredictionResult
from ml_model_strategy.domain.exceptions import FeatureMismatchError
from ml_model_strategy.domain.interfaces import MLModelStrategy


class DecisionTreeStrategy(MLModelStrategy):
    def predict(self, features: list[float]) -> PredictionResult:
        if len(features) != self.get_feature_count():
            raise FeatureMismatchError(self.get_feature_count(), len(features))

        size, age, location_score = features

        if size >= 100:
            price = 300_000.0 if location_score >= 7 else 220_000.0
        else:
            price = 180_000.0 if location_score >= 7 else 130_000.0

        if age > 30:
            price *= 0.85

        return PredictionResult(
            model_name=self.get_name(), prediction=price, confidence=0.65
        )

    def get_name(self) -> str:
        return "decision_tree"

    def get_feature_count(self) -> int:
        return 3
