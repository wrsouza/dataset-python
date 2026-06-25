"""Concrete `ModelLoader` implementations.

MockModelLoader simulates loading a heavy ML artifact (no real ML occurs
in this educational project): it counts how many times `load()` actually
ran, which the registry uses to prove that loaded models are cached and
not reloaded for every prediction request.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from model_registry.domain.interfaces import LoadedModel


@dataclass
class _InMemoryModel:
    """Fake loaded model: deterministic pseudo-prediction, no real ML."""

    model_name: str
    version: str

    def predict(self, payload: dict[str, float]) -> float:
        """Return a deterministic score derived from input values.

        This is NOT a real model — it exists only to prove that a
        `LoadedModel` instance can be obtained and used after loading.
        """
        if not payload:
            return 0.0
        return sum(payload.values()) / len(payload)


@dataclass
class MockModelLoader:
    """Simulates an expensive model-loading operation.

    `load_count` lets tests/UI assert that the registry calls `load()`
    only once per (model_name, version) — the whole point of caching
    loaded models inside a Singleton.
    """

    load_count: int = field(default=0, init=False)

    def load(self, model_name: str, version: str) -> LoadedModel:
        """Simulate loading weights into memory and return a usable model."""
        self.load_count += 1
        return _InMemoryModel(model_name=model_name, version=version)
