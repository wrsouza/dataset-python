"""Unit tests for domain entities: ModelMetrics, ModelVersion."""

from __future__ import annotations

import pytest

from model_registry.domain.entities import (
    ModelMetrics,
    ModelStatus,
    ModelVersion,
)


class TestModelMetrics:
    def test_valid_metrics(self) -> None:
        metrics = ModelMetrics(accuracy=0.9, f1_score=0.85, latency_ms=10.0)
        assert metrics.accuracy == 0.9

    def test_rejects_accuracy_above_one(self) -> None:
        with pytest.raises(ValueError, match="accuracy"):
            ModelMetrics(accuracy=1.5, f1_score=0.5, latency_ms=1.0)

    def test_rejects_negative_accuracy(self) -> None:
        with pytest.raises(ValueError, match="accuracy"):
            ModelMetrics(accuracy=-0.1, f1_score=0.5, latency_ms=1.0)

    def test_rejects_f1_score_out_of_range(self) -> None:
        with pytest.raises(ValueError, match="f1_score"):
            ModelMetrics(accuracy=0.5, f1_score=1.2, latency_ms=1.0)

    def test_rejects_negative_latency(self) -> None:
        with pytest.raises(ValueError, match="latency_ms"):
            ModelMetrics(accuracy=0.5, f1_score=0.5, latency_ms=-1.0)


class TestModelVersion:
    def _build(self, status: ModelStatus = ModelStatus.STAGING) -> ModelVersion:
        return ModelVersion(
            model_name="fraud-detector",
            version="v1.0.0",
            metrics=ModelMetrics(accuracy=0.9, f1_score=0.85, latency_ms=10.0),
            framework="scikit-learn",
            status=status,
        )

    def test_qualified_name(self) -> None:
        model_version = self._build()
        assert model_version.qualified_name == "fraud-detector:v1.0.0"

    def test_promote_sets_status_to_production(self) -> None:
        model_version = self._build()
        model_version.promote()
        assert model_version.status == ModelStatus.PRODUCTION

    def test_archive_sets_status_to_archived(self) -> None:
        model_version = self._build(status=ModelStatus.PRODUCTION)
        model_version.archive()
        assert model_version.status == ModelStatus.ARCHIVED

    def test_to_dict_contains_all_fields(self) -> None:
        model_version = self._build()
        data = model_version.to_dict()
        assert data["model_name"] == "fraud-detector"
        assert data["version"] == "v1.0.0"
        assert data["framework"] == "scikit-learn"
        assert data["status"] == "staging"
        assert data["metrics"] == {
            "accuracy": 0.9,
            "f1_score": 0.85,
            "latency_ms": 10.0,
        }

    def test_default_tags_is_empty_list(self) -> None:
        model_version = self._build()
        assert model_version.tags == []
