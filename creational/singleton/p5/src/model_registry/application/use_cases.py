"""Use cases orchestrating the ML Model Registry.

DIP: every use case depends only on `ModelRegistry`'s public methods, which
are themselves defined against the `ModelLoader` Protocol indirectly (the
registry never exposes the concrete loader). The Streamlit layer is the
only place that knows about `MockModelLoader`.
"""

from __future__ import annotations

from dataclasses import dataclass

from model_registry.domain.entities import ModelMetrics, ModelVersion
from model_registry.domain.interfaces import LoadedModel
from model_registry.infrastructure.registry import ModelRegistry


@dataclass
class RegisterModelVersionUseCase:
    """Registers a new model version as STAGING."""

    registry: ModelRegistry

    def execute(
        self,
        model_name: str,
        version: str,
        framework: str,
        accuracy: float,
        f1_score: float,
        latency_ms: float,
        tags: list[str] | None = None,
    ) -> ModelVersion:
        """Build a ModelVersion from raw fields and register it.

        Returns:
            The newly registered ModelVersion (status STAGING).
        """
        model_version = ModelVersion(
            model_name=model_name,
            version=version,
            metrics=ModelMetrics(
                accuracy=accuracy, f1_score=f1_score, latency_ms=latency_ms
            ),
            framework=framework,
            tags=list(tags or []),
        )
        self.registry.register_version(model_version)
        return model_version


@dataclass
class PromoteModelVersionUseCase:
    """Promotes a registered version to PRODUCTION."""

    registry: ModelRegistry

    def execute(self, model_name: str, version: str) -> ModelVersion:
        """Promote `version` of `model_name`, archiving the prior production."""
        return self.registry.promote_to_production(model_name, version)


@dataclass
class ListModelVersionsUseCase:
    """Lists all registered versions, optionally for a single model."""

    registry: ModelRegistry

    def execute(self, model_name: str | None = None) -> list[ModelVersion]:
        """Return the registered versions matching the optional filter."""
        return self.registry.list_versions(model_name)


@dataclass
class GetActiveModelUseCase:
    """Retrieves and loads (or reuses) the PRODUCTION model for inference."""

    registry: ModelRegistry

    def execute(self, model_name: str) -> LoadedModel:
        """Return a ready-to-use LoadedModel for the current production version.

        Demonstrates the Singleton's purpose: across many calls, the heavy
        `loader.load()` step only runs once per (model_name, version).
        """
        production_version = self.registry.get_production_version(model_name)
        return self.registry.get_loaded_model(model_name, production_version.version)
