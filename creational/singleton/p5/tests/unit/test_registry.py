"""Unit tests for ModelRegistry — singleton identity, registration, promotion.

Key assertions:
- Multiple calls to ModelRegistry(...) return the SAME object (identity, `is`).
- 50 concurrent threads racing to obtain the registry get the same object.
- Registration rejects duplicate (model_name, version) pairs.
- Promotion archives any previous PRODUCTION version of the same model.
- get_loaded_model() only invokes the loader once per version (caching proof).
"""

from __future__ import annotations

import threading
from typing import Any

import pytest

from model_registry.domain.entities import (
    DuplicateVersionError,
    ModelMetrics,
    ModelNotFoundError,
    ModelStatus,
    ModelVersion,
)
from model_registry.infrastructure.loaders import MockModelLoader
from model_registry.infrastructure.registry import ModelRegistry, SingletonMeta


@pytest.fixture(autouse=True)
def reset_singleton() -> Any:
    """Clear the singleton registry before and after every test."""
    SingletonMeta._instances.pop(ModelRegistry, None)
    yield
    SingletonMeta._instances.pop(ModelRegistry, None)


@pytest.fixture
def loader() -> MockModelLoader:
    return MockModelLoader()


def _make_version(
    model_name: str = "fraud-detector",
    version: str = "v1.0.0",
    status: ModelStatus = ModelStatus.STAGING,
) -> ModelVersion:
    return ModelVersion(
        model_name=model_name,
        version=version,
        metrics=ModelMetrics(accuracy=0.9, f1_score=0.85, latency_ms=10.0),
        framework="scikit-learn",
        status=status,
    )


# ── Singleton identity tests ──────────────────────────────────────────────────


def test_same_instance_on_repeated_calls(loader: MockModelLoader) -> None:
    """Two successive calls to ModelRegistry() return the same object."""
    first = ModelRegistry(loader=loader)
    second = ModelRegistry(loader=loader)
    assert first is second, "Singleton violated: two distinct instances created"


def test_same_instance_three_references(loader: MockModelLoader) -> None:
    """id() is identical for all references to the singleton."""
    a = ModelRegistry(loader=loader)
    b = ModelRegistry(loader=loader)
    c = ModelRegistry(loader=loader)
    assert id(a) == id(b) == id(c)


def test_singleton_under_thread_contention(loader: MockModelLoader) -> None:
    """50 threads racing to obtain the singleton must all get the same object."""
    instances: list[ModelRegistry] = []
    lock = threading.Lock()

    def grab() -> None:
        instance = ModelRegistry(loader=loader)
        with lock:
            instances.append(instance)

    threads = [threading.Thread(target=grab) for _ in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(instances) == 50
    first = instances[0]
    assert all(
        inst is first for inst in instances
    ), "Thread-safety violated: multiple distinct ModelRegistry instances created"


def test_instance_id_matches_python_id(loader: MockModelLoader) -> None:
    registry = ModelRegistry(loader=loader)
    assert registry.instance_id() == id(registry)


# ── Registration ──────────────────────────────────────────────────────────────


def test_register_version_adds_to_list(loader: MockModelLoader) -> None:
    registry = ModelRegistry(loader=loader)
    registry.register_version(_make_version())
    versions = registry.list_versions()
    assert len(versions) == 1
    assert versions[0].qualified_name == "fraud-detector:v1.0.0"


def test_register_duplicate_version_raises(loader: MockModelLoader) -> None:
    registry = ModelRegistry(loader=loader)
    registry.register_version(_make_version())
    with pytest.raises(DuplicateVersionError):
        registry.register_version(_make_version())


def test_list_versions_filters_by_model_name(loader: MockModelLoader) -> None:
    registry = ModelRegistry(loader=loader)
    registry.register_version(_make_version(model_name="fraud-detector"))
    registry.register_version(_make_version(model_name="churn-predictor"))
    filtered = registry.list_versions(model_name="churn-predictor")
    assert len(filtered) == 1
    assert filtered[0].model_name == "churn-predictor"


# ── Promotion ─────────────────────────────────────────────────────────────────


def test_promote_to_production_sets_status(loader: MockModelLoader) -> None:
    registry = ModelRegistry(loader=loader)
    registry.register_version(_make_version())
    promoted = registry.promote_to_production("fraud-detector", "v1.0.0")
    assert promoted.status == ModelStatus.PRODUCTION


def test_promote_unknown_version_raises(loader: MockModelLoader) -> None:
    registry = ModelRegistry(loader=loader)
    with pytest.raises(ModelNotFoundError):
        registry.promote_to_production("fraud-detector", "v9.9.9")


def test_promoting_new_version_archives_previous_production(
    loader: MockModelLoader,
) -> None:
    registry = ModelRegistry(loader=loader)
    registry.register_version(_make_version(version="v1.0.0"))
    registry.register_version(_make_version(version="v2.0.0"))

    registry.promote_to_production("fraud-detector", "v1.0.0")
    registry.promote_to_production("fraud-detector", "v2.0.0")

    v1 = next(v for v in registry.list_versions() if v.version == "v1.0.0")
    v2 = next(v for v in registry.list_versions() if v.version == "v2.0.0")
    assert v1.status == ModelStatus.ARCHIVED
    assert v2.status == ModelStatus.PRODUCTION


def test_get_production_version_returns_promoted(loader: MockModelLoader) -> None:
    registry = ModelRegistry(loader=loader)
    registry.register_version(_make_version())
    registry.promote_to_production("fraud-detector", "v1.0.0")
    production = registry.get_production_version("fraud-detector")
    assert production.version == "v1.0.0"


def test_get_production_version_raises_when_none_promoted(
    loader: MockModelLoader,
) -> None:
    registry = ModelRegistry(loader=loader)
    registry.register_version(_make_version())
    with pytest.raises(ModelNotFoundError):
        registry.get_production_version("fraud-detector")


# ── Loaded model cache ─────────────────────────────────────────────────────────


def test_get_loaded_model_caches_across_calls(loader: MockModelLoader) -> None:
    registry = ModelRegistry(loader=loader)
    registry.register_version(_make_version())

    registry.get_loaded_model("fraud-detector", "v1.0.0")
    registry.get_loaded_model("fraud-detector", "v1.0.0")
    registry.get_loaded_model("fraud-detector", "v1.0.0")

    assert loader.load_count == 1, "loader.load() must run only once per version"


def test_get_loaded_model_unknown_version_raises(loader: MockModelLoader) -> None:
    registry = ModelRegistry(loader=loader)
    with pytest.raises(ModelNotFoundError):
        registry.get_loaded_model("fraud-detector", "v1.0.0")


def test_loaded_model_count_reflects_distinct_versions(
    loader: MockModelLoader,
) -> None:
    registry = ModelRegistry(loader=loader)
    registry.register_version(_make_version(version="v1.0.0"))
    registry.register_version(_make_version(version="v2.0.0"))

    registry.get_loaded_model("fraud-detector", "v1.0.0")
    registry.get_loaded_model("fraud-detector", "v2.0.0")

    assert registry.loaded_model_count() == 2


# ── Thread-safety: concurrent reads and writes ────────────────────────────────


def test_concurrent_registration_does_not_corrupt_state(
    loader: MockModelLoader,
) -> None:
    registry = ModelRegistry(loader=loader)
    errors: list[Exception] = []

    def register(version_suffix: int) -> None:
        try:
            registry.register_version(_make_version(version=f"v{version_suffix}"))
        except Exception as exc:  # noqa: BLE001 - collected for assertion
            errors.append(exc)

    threads = [threading.Thread(target=register, args=(i,)) for i in range(30)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Concurrent registration errors: {errors}"
    assert len(registry.list_versions()) == 30


def test_concurrent_get_loaded_model_loads_once(loader: MockModelLoader) -> None:
    registry = ModelRegistry(loader=loader)
    registry.register_version(_make_version())
    errors: list[Exception] = []

    def fetch() -> None:
        try:
            registry.get_loaded_model("fraud-detector", "v1.0.0")
        except Exception as exc:  # noqa: BLE001 - collected for assertion
            errors.append(exc)

    threads = [threading.Thread(target=fetch) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Concurrent get_loaded_model errors: {errors}"
    assert loader.load_count == 1
