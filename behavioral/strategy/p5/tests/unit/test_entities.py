"""Unit tests for the PredictionResult domain entity."""

from __future__ import annotations

import pytest

from ml_model_strategy.domain.entities import PredictionResult


def test_rejects_confidence_outside_0_1() -> None:
    with pytest.raises(ValueError, match="confidence"):
        PredictionResult(model_name="x", prediction=1.0, confidence=1.5)
