"""Domain entities for the ML Model Strategy demo."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PredictionResult:
    """Immutable outcome of running a model over a feature vector."""

    model_name: str
    prediction: float
    confidence: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {self.confidence}")
