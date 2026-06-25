"""Integration test: full workflow through application use cases.

Exercises register -> list -> promote -> get_active_model end-to-end,
using the same ModelRegistry singleton and MockModelLoader the Streamlit
UI uses, but driving it directly through the application layer.
"""

from __future__ import annotations

from typing import Any

import pytest

from model_registry.application.use_cases import (
    GetActiveModelUseCase,
    ListModelVersionsUseCase,
    PromoteModelVersionUseCase,
    RegisterModelVersionUseCase,
)
from model_registry.domain.entities import ModelNotFoundError, ModelStatus
from model_registry.infrastructure.loaders import MockModelLoader
from model_registry.infrastructure.registry import ModelRegistry, SingletonMeta


@pytest.fixture(autouse=True)
def reset_singleton() -> Any:
    """Clear the singleton registry before and after every test."""
    SingletonMeta._instances.pop(ModelRegistry, None)
    yield
    SingletonMeta._instances.pop(ModelRegistry, None)


def test_full_register_promote_infer_workflow() -> None:
    loader = MockModelLoader()
    registry = ModelRegistry(loader=loader)

    register_use_case = RegisterModelVersionUseCase(registry)
    list_use_case = ListModelVersionsUseCase(registry)
    promote_use_case = PromoteModelVersionUseCase(registry)
    get_active_use_case = GetActiveModelUseCase(registry)

    register_use_case.execute(
        model_name="fraud-detector",
        version="v1.0.0",
        framework="scikit-learn",
        accuracy=0.9,
        f1_score=0.85,
        latency_ms=12.0,
        tags=["tabular"],
    )
    register_use_case.execute(
        model_name="fraud-detector",
        version="v2.0.0",
        framework="xgboost",
        accuracy=0.93,
        f1_score=0.9,
        latency_ms=9.0,
    )

    versions = list_use_case.execute(model_name="fraud-detector")
    assert len(versions) == 2

    promote_use_case.execute("fraud-detector", "v2.0.0")

    model = get_active_use_case.execute("fraud-detector")
    score = model.predict({"amount": 50.0, "age": 30.0})
    assert score == 40.0

    refreshed = list_use_case.execute(model_name="fraud-detector")
    promoted = next(v for v in refreshed if v.version == "v2.0.0")
    assert promoted.status == ModelStatus.PRODUCTION
    assert loader.load_count == 1


def test_get_active_model_without_promotion_raises() -> None:
    loader = MockModelLoader()
    registry = ModelRegistry(loader=loader)
    register_use_case = RegisterModelVersionUseCase(registry)
    get_active_use_case = GetActiveModelUseCase(registry)

    register_use_case.execute(
        model_name="churn-predictor",
        version="v1.0.0",
        framework="pytorch",
        accuracy=0.8,
        f1_score=0.78,
        latency_ms=15.0,
    )

    with pytest.raises(ModelNotFoundError):
        get_active_use_case.execute("churn-predictor")


def test_repeated_inference_reuses_cached_loaded_model() -> None:
    loader = MockModelLoader()
    registry = ModelRegistry(loader=loader)
    register_use_case = RegisterModelVersionUseCase(registry)
    promote_use_case = PromoteModelVersionUseCase(registry)
    get_active_use_case = GetActiveModelUseCase(registry)

    register_use_case.execute(
        model_name="fraud-detector",
        version="v1.0.0",
        framework="scikit-learn",
        accuracy=0.9,
        f1_score=0.85,
        latency_ms=12.0,
    )
    promote_use_case.execute("fraud-detector", "v1.0.0")

    for _ in range(5):
        get_active_use_case.execute("fraud-detector")

    assert loader.load_count == 1, "loader.load() must run only once"


def test_use_cases_share_the_same_singleton_registry() -> None:
    """Two independently constructed use cases see the same registry state."""
    loader = MockModelLoader()
    register_use_case = RegisterModelVersionUseCase(ModelRegistry(loader=loader))
    list_use_case = ListModelVersionsUseCase(ModelRegistry(loader=loader))

    register_use_case.execute(
        model_name="fraud-detector",
        version="v1.0.0",
        framework="scikit-learn",
        accuracy=0.9,
        f1_score=0.85,
        latency_ms=12.0,
    )

    assert len(list_use_case.execute()) == 1
