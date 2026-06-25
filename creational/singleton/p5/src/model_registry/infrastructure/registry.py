"""Singleton ML Model Registry.

Pattern: Singleton via metaclass with double-checked locking.

Why a metaclass (instead of a module-level instance or `__new__` + lock)?
  - It keeps the singleton machinery (`SingletonMeta`) completely separate
    from business logic (`ModelRegistry`), which is the cleanest expression
    of SRP among the three common approaches.
  - Unlike a bare module-level singleton, it works uniformly for any class
    we later want to make a Singleton (consistent with the convention
    already used by the sibling project `singleton/p3`), and it does not
    rely on import-time side effects, which are easy to break by an
    unexpected `importlib.reload` or by importing the module under two
    different names.
  - Compared to `__new__` + lock alone, this approach lets `__init__`
    remain straightforward (no manual short-circuiting needed beyond the
    `_initialized` guard), because the metaclass is solely responsible for
    deciding whether to construct a new instance at all.

Why is it thread-safe?
  `SingletonMeta.__call__` uses double-checked locking: the *first* check
  (`cls not in cls._instances`) is a fast, lock-free read. If a thread sees
  the class is not yet instantiated, it acquires `_lock` and checks again
  *inside* the critical section before constructing the instance. Only the
  thread that wins the race actually builds the object; every other thread
  (including ones that lost the original race) returns the same cached
  instance. Without the second check, two threads could both pass the first
  check and each construct a separate instance before either reached the
  lock.

  In addition, `ModelRegistry` protects its own mutable state (`_versions`,
  `_loaded_models`, `_instance_count`) with a `threading.RLock`, since
  Streamlit can invoke use cases from multiple script reruns/sessions
  concurrently, and registration/promotion must remain atomic.
"""

from __future__ import annotations

import threading
from typing import Any, ClassVar

from model_registry.domain.entities import (
    DuplicateVersionError,
    ModelNotFoundError,
    ModelStatus,
    ModelVersion,
)
from model_registry.domain.interfaces import LoadedModel, ModelLoader


class SingletonMeta(type):
    """Metaclass enforcing one instance per class via double-checked locking."""

    _instances: ClassVar[dict[type, Any]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class ModelRegistry(metaclass=SingletonMeta):
    """The single in-memory source of truth for registered ML models.

    SRP: this class owns model metadata and the cache of loaded model
    instances, plus the promotion rule (only one PRODUCTION version per
    model name). It does not know how models are loaded (DIP: that is
    delegated to an injected `ModelLoader`) or how results are displayed
    (left entirely to the Streamlit layer).
    """

    def __init__(self, loader: ModelLoader) -> None:
        # SingletonMeta guarantees __init__ runs only once for this class,
        # but the guard documents the contract explicitly and protects
        # against accidental direct instantiation bypassing the metaclass.
        if getattr(self, "_initialized", False):
            return
        self._loader = loader
        self._versions: dict[str, ModelVersion] = {}
        self._loaded_models: dict[str, LoadedModel] = {}
        self._rlock = threading.RLock()
        self._instance_count = 1
        self._initialized = True

    # ── Registration ──────────────────────────────────────────────────────

    def register_version(self, model_version: ModelVersion) -> None:
        """Register a new model version as STAGING.

        Raises:
            DuplicateVersionError: if this (model_name, version) already exists.
        """
        with self._rlock:
            key = model_version.qualified_name
            if key in self._versions:
                raise DuplicateVersionError(
                    model_version.model_name, model_version.version
                )
            self._versions[key] = model_version

    # ── Promotion ─────────────────────────────────────────────────────────

    def promote_to_production(self, model_name: str, version: str) -> ModelVersion:
        """Promote `version` to PRODUCTION, archiving any prior production version.

        Enforces the invariant: at most one PRODUCTION version per model_name.

        Raises:
            ModelNotFoundError: if the (model_name, version) is not registered.
        """
        with self._rlock:
            target = self._get_version(model_name, version)
            for existing in self._versions.values():
                if (
                    existing.model_name == model_name
                    and existing.status == ModelStatus.PRODUCTION
                ):
                    existing.archive()
            target.promote()
            return target

    # ── Queries ───────────────────────────────────────────────────────────

    def list_versions(self, model_name: str | None = None) -> list[ModelVersion]:
        """List all registered versions, optionally filtered by model name."""
        with self._rlock:
            versions = list(self._versions.values())
        if model_name is None:
            return versions
        return [v for v in versions if v.model_name == model_name]

    def get_production_version(self, model_name: str) -> ModelVersion:
        """Return the current PRODUCTION version of `model_name`.

        Raises:
            ModelNotFoundError: if no version of `model_name` is in PRODUCTION.
        """
        with self._rlock:
            for version in self._versions.values():
                if (
                    version.model_name == model_name
                    and version.status == ModelStatus.PRODUCTION
                ):
                    return version
        raise ModelNotFoundError(model_name, "production")

    # ── Loaded model cache ────────────────────────────────────────────────

    def get_loaded_model(self, model_name: str, version: str) -> LoadedModel:
        """Return a cached LoadedModel, loading it via `ModelLoader` once.

        This is the core MLOps benefit of the Singleton: repeated calls for
        the same (model_name, version) never re-trigger `loader.load()`.
        """
        with self._rlock:
            self._get_version(model_name, version)  # validates existence
            key = f"{model_name}:{version}"
            if key not in self._loaded_models:
                self._loaded_models[key] = self._loader.load(model_name, version)
            return self._loaded_models[key]

    def loaded_model_count(self) -> int:
        """Number of distinct model versions currently cached in memory."""
        with self._rlock:
            return len(self._loaded_models)

    def instance_id(self) -> int:
        """Return `id(self)` — visual proof that the same object is reused."""
        return id(self)

    # ── Private helpers ───────────────────────────────────────────────────

    def _get_version(self, model_name: str, version: str) -> ModelVersion:
        key = f"{model_name}:{version}"
        found = self._versions.get(key)
        if found is None:
            raise ModelNotFoundError(model_name, version)
        return found
