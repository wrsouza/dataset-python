"""ModelPredictor context — uses MLModelStrategy via composition, swappable
at runtime."""

from __future__ import annotations

from ml_model_strategy.domain.entities import PredictionResult
from ml_model_strategy.domain.interfaces import MLModelStrategy


class NoStrategyConfiguredError(Exception):
    def __init__(self) -> None:
        super().__init__("No model strategy configured")


class ModelPredictor:
    """Context that delegates inference to a pluggable MLModelStrategy.

    DIP: depends on MLModelStrategy ABC, not concrete implementations.
    """

    def __init__(self, strategy: MLModelStrategy | None = None) -> None:
        self._strategy: MLModelStrategy | None = strategy

    def set_strategy(self, strategy: MLModelStrategy) -> None:
        self._strategy = strategy

    @property
    def current_strategy(self) -> MLModelStrategy | None:
        return self._strategy

    def predict(self, features: list[float]) -> PredictionResult:
        """Delegate inference to the configured strategy.

        Raises:
            NoStrategyConfiguredError: when no strategy has been set.
        """
        if self._strategy is None:
            raise NoStrategyConfiguredError()
        return self._strategy.predict(features)
