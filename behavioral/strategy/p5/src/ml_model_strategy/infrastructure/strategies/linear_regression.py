"""LinearRegressionStrategy — a hand-rolled weighted sum, no training involved.

The point of this dataset entry is the Strategy pattern, not a real ML
pipeline — weights are fixed constants standing in for a model that
would otherwise be trained offline and loaded here.
"""

from __future__ import annotations

from ml_model_strategy.domain.entities import PredictionResult
from ml_model_strategy.domain.exceptions import FeatureMismatchError
from ml_model_strategy.domain.interfaces import MLModelStrategy

_WEIGHTS = [120.0, -2.5, 15.0]  # size (m^2), age (years), location_score (0-10)
_BIAS = 50_000.0


class LinearRegressionStrategy(MLModelStrategy):
    def predict(self, features: list[float]) -> PredictionResult:
        if len(features) != self.get_feature_count():
            raise FeatureMismatchError(self.get_feature_count(), len(features))

        price = sum(w * f for w, f in zip(_WEIGHTS, features, strict=True)) + _BIAS
        return PredictionResult(
            model_name=self.get_name(), prediction=price, confidence=0.75
        )

    def get_name(self) -> str:
        return "linear_regression"

    def get_feature_count(self) -> int:
        return 3
