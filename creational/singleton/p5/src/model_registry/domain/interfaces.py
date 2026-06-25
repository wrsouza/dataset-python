"""Domain interfaces (Protocols) for the ML Model Registry.

OCP: `ModelLoader` is a Protocol — new loading strategies (e.g. loading from
S3, from a local pickle, from an ONNX runtime) can be added by writing a new
class that satisfies this Protocol, with zero changes to the registry or to
the use cases that depend on it (DIP: application depends on the
abstraction, never on a concrete loader).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LoadedModel(Protocol):
    """A model artifact that has been loaded into memory.

    Kept intentionally minimal (Interface Segregation): callers only need
    to invoke `predict`, not the internals of any specific ML framework.
    """

    def predict(self, payload: dict[str, float]) -> float:
        """Run inference on a single input payload and return a score."""
        ...


@runtime_checkable
class ModelLoader(Protocol):
    """Strategy for turning a (model_name, version) pair into a LoadedModel.

    Implementations simulate the expensive part of MLOps (downloading
    weights, allocating GPU memory, etc.) that the Singleton registry
    exists to avoid repeating unnecessarily.
    """

    def load(self, model_name: str, version: str) -> LoadedModel:
        """Load (or simulate loading) the given model version into memory."""
        ...
