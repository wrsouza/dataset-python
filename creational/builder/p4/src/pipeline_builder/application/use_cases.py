"""Application layer — Director and use-case orchestration for Pipeline Builder."""
from __future__ import annotations

from typing import Any

from pipeline_builder.domain.entities import Pipeline
from pipeline_builder.domain.interfaces import PipelineBuilder


class ETLDirector:
    """Director: orchestrates the builder to produce standard pipeline blueprints.

    DIP: depends on the PipelineBuilder abstraction, not on any concrete builder.
    """

    def __init__(self, builder: PipelineBuilder) -> None:
        self._builder = builder

    # ------------------------------------------------------------------
    # Pre-defined pipeline recipes
    # ------------------------------------------------------------------

    def build_standard_etl(self, source_config: dict[str, Any]) -> Pipeline:
        """Builds: source → deduplicate → sort(id) → sink(console).

        The most common ETL pattern: load, deduplicate, and sort the data.
        """
        return (
            self._builder
            .add_source(source_config)
            .add_transform("deduplicate", {})
            .add_transform("sort", {"column": "id", "descending": False})
            .add_sink({"destination": "console", "format": "table"})
            .build()
        )

    def build_validation_pipeline(
        self,
        source_config: dict[str, Any],
        filter_condition: str,
    ) -> Pipeline:
        """Builds: source → filter(condition) → sink(report).

        Used for data-quality checks: load data and flag rows that fail
        a business rule expressed as a filter condition.
        """
        return (
            self._builder
            .add_source(source_config)
            .add_filter(filter_condition)
            .add_sink({"destination": "report", "format": "json"})
            .build()
        )

    def build_aggregation_pipeline(
        self,
        source_config: dict[str, Any],
        group_by: str,
        agg_column: str,
    ) -> Pipeline:
        """Builds: source → aggregate(group_by, sum) → sort(desc) → sink.

        Produces grouped summary statistics from the raw dataset.
        """
        return (
            self._builder
            .add_source(source_config)
            .add_transform("aggregate", {"group_by": group_by, "agg_column": agg_column})
            .add_transform("sort", {"column": f"sum_{agg_column}", "descending": True})
            .add_sink({"destination": "dashboard", "format": "chart"})
            .build()
        )


class BuildPipelineUseCase:
    """Use case for building a custom pipeline from a step specification list.

    Accepts a list of step dicts from the UI and delegates to the builder.
    """

    def __init__(self, builder: PipelineBuilder) -> None:
        self._builder = builder

    def execute(self, steps: list[dict[str, Any]]) -> Pipeline:
        """Build a pipeline from a list of step descriptors.

        Each step dict must have a 'type' key and optional 'config'/'params'.
        """
        for step in steps:
            step_type = step.get("type", "")
            config: dict[str, Any] = step.get("config", {})

            if step_type == "source":
                self._builder.add_source(config)
            elif step_type == "transform":
                self._builder.add_transform(
                    config.get("transform_type", "sort"),
                    {k: v for k, v in config.items() if k != "transform_type"},
                )
            elif step_type == "filter":
                self._builder.add_filter(config.get("condition", ""))
            elif step_type == "sink":
                self._builder.add_sink(config)
            else:
                raise ValueError(f"Unknown step type: '{step_type}'")

        return self._builder.build()
