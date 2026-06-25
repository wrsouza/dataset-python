"""Strategy ABC for the ML Model Strategy demo."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ml_model_strategy.domain.entities import PredictionResult


class MLModelStrategy(ABC):
    """Abstract base for all model strategies.

    OCP: add a new model = new subclass, no existing code changes.
    LSP: all subclasses return PredictionResult for the same feature
    vector shape (`get_feature_count()`).
    """

    @abstractmethod
    def predict(self, features: list[float]) -> PredictionResult:
        """Run inference over a feature vector."""
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Return the canonical name of this model."""
        ...

    @abstractmethod
    def get_feature_count(self) -> int:
        """Return how many input features this model expects."""
        ...
