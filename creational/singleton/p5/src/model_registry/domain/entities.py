"""Domain entities for the ML Model Registry.

These are plain value objects with no dependency on Streamlit, threading,
or any concrete storage/loading mechanism (SRP: only describe model data).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ModelStatus(StrEnum):
    """Lifecycle status of a registered model version."""

    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


class ModelNotFoundError(Exception):
    """Raised when a requested model name/version does not exist."""

    def __init__(self, model_name: str, version: str | None = None) -> None:
        self.model_name = model_name
        self.version = version
        target = f"{model_name}:{version}" if version else model_name
        super().__init__(f"Model '{target}' not found in registry")


class DuplicateVersionError(Exception):
    """Raised when registering a version that already exists for a model."""

    def __init__(self, model_name: str, version: str) -> None:
        self.model_name = model_name
        self.version = version
        super().__init__(
            f"Version '{version}' already registered for model '{model_name}'"
        )


@dataclass(frozen=True)
class ModelMetrics:
    """Evaluation metrics captured at training/validation time."""

    accuracy: float
    f1_score: float
    latency_ms: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.accuracy <= 1.0:
            raise ValueError("accuracy must be between 0.0 and 1.0")
        if not 0.0 <= self.f1_score <= 1.0:
            raise ValueError("f1_score must be between 0.0 and 1.0")
        if self.latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")


@dataclass
class ModelVersion:
    """A single registered version of a named ML model.

    SRP: describes WHAT a model version is (metadata + lifecycle status).
    It knows nothing about how it is loaded into memory or how the
    registry enforces promotion rules — that is the registry's job.
    """

    model_name: str
    version: str
    metrics: ModelMetrics
    framework: str
    status: ModelStatus = ModelStatus.STAGING
    tags: list[str] = field(default_factory=list)

    @property
    def qualified_name(self) -> str:
        """Unique identifier combining model name and version."""
        return f"{self.model_name}:{self.version}"

    def promote(self) -> None:
        """Mark this version as the production version."""
        self.status = ModelStatus.PRODUCTION

    def archive(self) -> None:
        """Mark this version as archived (no longer production-eligible)."""
        self.status = ModelStatus.ARCHIVED

    def to_dict(self) -> dict[str, object]:
        """Serialize to a JSON-friendly dictionary for UI rendering."""
        return {
            "model_name": self.model_name,
            "version": self.version,
            "framework": self.framework,
            "status": self.status.value,
            "tags": list(self.tags),
            "metrics": {
                "accuracy": self.metrics.accuracy,
                "f1_score": self.metrics.f1_score,
                "latency_ms": self.metrics.latency_ms,
            },
        }
