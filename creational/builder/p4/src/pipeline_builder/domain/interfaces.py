"""Abstract Builder interface for the Pipeline Builder pattern."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pipeline_builder.domain.entities import Pipeline, SourceFormat


class PipelineBuilder(ABC):
    """Builder interface for constructing data pipelines step by step.

    Each concrete builder specialises the source format (CSV, JSON, API)
    while exposing the same construction API to the Director.

    SRP: this class owns only the pipeline construction contract.
    OCP: new source types extend via a new ConcreteBuilder, not modification.
    """

    @abstractmethod
    def add_source(self, config: dict[str, Any]) -> "PipelineBuilder":
        """Configure the data source for this pipeline."""
        ...

    @abstractmethod
    def add_transform(self, transform_type: str, params: dict[str, Any]) -> "PipelineBuilder":
        """Add a transformation step (rename, cast, sort, aggregate, deduplicate)."""
        ...

    @abstractmethod
    def add_filter(self, condition: str) -> "PipelineBuilder":
        """Add a filter step that keeps only rows matching the condition."""
        ...

    @abstractmethod
    def add_sink(self, config: dict[str, Any]) -> "PipelineBuilder":
        """Configure the data sink (output destination)."""
        ...

    @abstractmethod
    def build(self) -> Pipeline:
        """Assemble and return the finished Pipeline product."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Clear all accumulated state so the builder can be reused."""
        ...

    @property
    @abstractmethod
    def source_format(self) -> SourceFormat:
        """Return the source format this builder handles."""
        ...
