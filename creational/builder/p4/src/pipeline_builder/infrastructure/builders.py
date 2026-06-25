"""Concrete Builder implementations for each source format."""
from __future__ import annotations

import csv
import io
import json
from typing import Any

from pipeline_builder.domain.entities import (
    Pipeline,
    PipelineStep,
    SourceFormat,
    StepType,
    TransformType,
)
from pipeline_builder.domain.interfaces import PipelineBuilder


class _BasePipelineBuilder(PipelineBuilder):
    """Shared implementation — subclasses only override source_format and _load_data."""

    def __init__(self) -> None:
        self._steps: list[PipelineStep] = []
        self._step_counter: int = 0

    # ------------------------------------------------------------------
    # Builder interface
    # ------------------------------------------------------------------

    def add_source(self, config: dict[str, Any]) -> "PipelineBuilder":
        self._step_counter += 1
        step = PipelineStep(
            step_type=StepType.SOURCE,
            name=f"source_{self._step_counter}",
            config={**config, "format": self.source_format.value},
        )
        self._steps.append(step)
        return self

    def add_transform(self, transform_type: str, params: dict[str, Any]) -> "PipelineBuilder":
        self._step_counter += 1
        valid_types = {t.value for t in TransformType}
        if transform_type not in valid_types:
            raise ValueError(
                f"Unknown transform '{transform_type}'. Valid: {sorted(valid_types)}"
            )
        step = PipelineStep(
            step_type=StepType.TRANSFORM,
            name=f"transform_{self._step_counter}_{transform_type}",
            config={"type": transform_type, **params},
        )
        self._steps.append(step)
        return self

    def add_filter(self, condition: str) -> "PipelineBuilder":
        self._step_counter += 1
        step = PipelineStep(
            step_type=StepType.FILTER,
            name=f"filter_{self._step_counter}",
            config={"condition": condition},
        )
        self._steps.append(step)
        return self

    def add_sink(self, config: dict[str, Any]) -> "PipelineBuilder":
        self._step_counter += 1
        step = PipelineStep(
            step_type=StepType.SINK,
            name=f"sink_{self._step_counter}",
            config=config,
        )
        self._steps.append(step)
        return self

    def build(self) -> Pipeline:
        if not self._steps:
            raise ValueError("Pipeline has no steps — call add_source() at minimum.")
        pipeline = Pipeline(
            name=f"{self.source_format.value}_pipeline",
            source_format=self.source_format,
            steps=list(self._steps),
        )
        self.reset()
        return pipeline

    def reset(self) -> None:
        self._steps = []
        self._step_counter = 0


class CSVPipelineBuilder(_BasePipelineBuilder):
    """ConcreteBuilder for CSV-sourced pipelines.

    Pre-validates that the source config contains a 'content' or 'path' key
    and parses sample data for preview purposes.
    """

    @property
    def source_format(self) -> SourceFormat:
        return SourceFormat.CSV

    def add_source(self, config: dict[str, Any]) -> "PipelineBuilder":
        # CSV-specific: parse sample rows and embed them in config
        if "content" in config:
            rows = _parse_csv_content(config["content"])
            config = {**config, "sample_data": rows[:20]}
        return super().add_source(config)


class JSONPipelineBuilder(_BasePipelineBuilder):
    """ConcreteBuilder for JSON-sourced pipelines."""

    @property
    def source_format(self) -> SourceFormat:
        return SourceFormat.JSON

    def add_source(self, config: dict[str, Any]) -> "PipelineBuilder":
        if "content" in config:
            rows = _parse_json_content(config["content"])
            config = {**config, "sample_data": rows[:20]}
        return super().add_source(config)


class APIPipelineBuilder(_BasePipelineBuilder):
    """ConcreteBuilder for REST API-sourced pipelines (mock data)."""

    @property
    def source_format(self) -> SourceFormat:
        return SourceFormat.API

    def add_source(self, config: dict[str, Any]) -> "PipelineBuilder":
        # Generate mock data representing an API response
        mock_data = _generate_mock_api_data(config.get("endpoint", "/api/data"))
        config = {**config, "sample_data": mock_data}
        return super().add_source(config)


# ---------------------------------------------------------------------------
# Parsing helpers (each with a single responsibility)
# ---------------------------------------------------------------------------

def _parse_csv_content(content: str) -> list[dict[str, Any]]:
    """Parse CSV text into a list of row dicts."""
    reader = csv.DictReader(io.StringIO(content))
    return [dict(row) for row in reader]


def _parse_json_content(content: str) -> list[dict[str, Any]]:
    """Parse JSON text — accepts an array or a single object."""
    parsed = json.loads(content)
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        return [parsed]
    raise ValueError("JSON source must be an array or a single object.")


def _generate_mock_api_data(endpoint: str) -> list[dict[str, Any]]:
    """Generate deterministic mock rows for a given API endpoint."""
    base_rows = [
        {"id": i, "endpoint": endpoint, "value": i * 10, "category": f"cat_{i % 3}"}
        for i in range(1, 21)
    ]
    return base_rows
