"""Unit tests for MockModelLoader."""

from __future__ import annotations

from model_registry.infrastructure.loaders import MockModelLoader


class TestMockModelLoader:
    def test_load_returns_a_predictable_model(self) -> None:
        loader = MockModelLoader()
        model = loader.load("fraud-detector", "v1.0.0")
        score = model.predict({"amount": 10.0, "age": 30.0})
        assert score == 20.0

    def test_load_increments_load_count(self) -> None:
        loader = MockModelLoader()
        loader.load("fraud-detector", "v1.0.0")
        loader.load("fraud-detector", "v2.0.0")
        assert loader.load_count == 2

    def test_predict_with_empty_payload_returns_zero(self) -> None:
        loader = MockModelLoader()
        model = loader.load("fraud-detector", "v1.0.0")
        assert model.predict({}) == 0.0
