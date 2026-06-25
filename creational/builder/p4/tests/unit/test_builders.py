"""Unit tests for Pipeline Builder — concrete builders and domain entities."""
from __future__ import annotations

import pytest

from pipeline_builder.application.use_cases import ETLDirector
from pipeline_builder.domain.entities import (
    Pipeline,
    SourceFormat,
    StepType,
)
from pipeline_builder.infrastructure.builders import (
    APIPipelineBuilder,
    CSVPipelineBuilder,
    JSONPipelineBuilder,
)

SAMPLE_CSV = (
    "id,name,category,amount\n"
    "1,Alice,A,100\n"
    "2,Bob,B,200\n"
    "3,Alice,A,150\n"
    "4,Carol,C,300\n"
    "2,Bob,B,200"
)
SAMPLE_JSON = (
    '[{"id":1,"name":"Alice","category":"A","amount":100},'
    '{"id":2,"name":"Bob","category":"B","amount":200}]'
)


# ---------------------------------------------------------------------------
# CSVPipelineBuilder
# ---------------------------------------------------------------------------

class TestCSVPipelineBuilder:
    def test_source_format_is_csv(self, csv_builder: CSVPipelineBuilder) -> None:
        assert csv_builder.source_format == SourceFormat.CSV

    def test_add_source_creates_step(self, csv_builder: CSVPipelineBuilder) -> None:
        pipeline = csv_builder.add_source({"content": SAMPLE_CSV}).build()
        assert any(s.step_type == StepType.SOURCE for s in pipeline.steps)

    def test_csv_source_parses_sample_data(self, csv_builder: CSVPipelineBuilder) -> None:
        pipeline = csv_builder.add_source({"content": SAMPLE_CSV}).build()
        source_step = next(s for s in pipeline.steps if s.step_type == StepType.SOURCE)
        assert "sample_data" in source_step.config
        assert len(source_step.config["sample_data"]) == 5

    def test_add_filter_appends_step(self, csv_builder: CSVPipelineBuilder) -> None:
        pipeline = (
            csv_builder
            .add_source({"content": SAMPLE_CSV})
            .add_filter("amount > 100")
            .build()
        )
        assert any(s.step_type == StepType.FILTER for s in pipeline.steps)

    def test_add_transform_sort(self, csv_builder: CSVPipelineBuilder) -> None:
        pipeline = (
            csv_builder
            .add_source({"content": SAMPLE_CSV})
            .add_transform("sort", {"column": "name"})
            .build()
        )
        assert any(s.step_type == StepType.TRANSFORM for s in pipeline.steps)

    def test_add_transform_invalid_type_raises(self, csv_builder: CSVPipelineBuilder) -> None:
        csv_builder.add_source({"content": SAMPLE_CSV})
        with pytest.raises(ValueError, match="Unknown transform"):
            csv_builder.add_transform("explode", {})

    def test_build_with_no_steps_raises(self, csv_builder: CSVPipelineBuilder) -> None:
        with pytest.raises(ValueError, match="no steps"):
            csv_builder.build()

    def test_reset_clears_steps(self, csv_builder: CSVPipelineBuilder) -> None:
        csv_builder.add_source({"content": SAMPLE_CSV})
        csv_builder.reset()
        with pytest.raises(ValueError):
            csv_builder.build()

    def test_build_then_build_again_raises_after_reset(
        self, csv_builder: CSVPipelineBuilder
    ) -> None:
        # build() implicitly resets — second build should fail
        csv_builder.add_source({"content": SAMPLE_CSV}).build()
        with pytest.raises(ValueError):
            csv_builder.build()

    def test_pipeline_name_matches_format(self, csv_builder: CSVPipelineBuilder) -> None:
        pipeline = csv_builder.add_source({"content": SAMPLE_CSV}).build()
        assert "csv" in pipeline.name

    def test_add_sink_appends_step(self, csv_builder: CSVPipelineBuilder) -> None:
        pipeline = (
            csv_builder
            .add_source({"content": SAMPLE_CSV})
            .add_sink({"destination": "console"})
            .build()
        )
        assert any(s.step_type == StepType.SINK for s in pipeline.steps)


# ---------------------------------------------------------------------------
# JSONPipelineBuilder
# ---------------------------------------------------------------------------

class TestJSONPipelineBuilder:
    def test_source_format_is_json(self, json_builder: JSONPipelineBuilder) -> None:
        assert json_builder.source_format == SourceFormat.JSON

    def test_json_source_parses_array(self, json_builder: JSONPipelineBuilder) -> None:
        pipeline = json_builder.add_source({"content": SAMPLE_JSON}).build()
        source_step = next(s for s in pipeline.steps if s.step_type == StepType.SOURCE)
        assert len(source_step.config["sample_data"]) == 2

    def test_json_source_wraps_single_object(self, json_builder: JSONPipelineBuilder) -> None:
        pipeline = json_builder.add_source(
            {"content": '{"id":1,"name":"Alice"}'}
        ).build()
        source_step = next(s for s in pipeline.steps if s.step_type == StepType.SOURCE)
        assert len(source_step.config["sample_data"]) == 1


# ---------------------------------------------------------------------------
# APIPipelineBuilder
# ---------------------------------------------------------------------------

class TestAPIPipelineBuilder:
    def test_source_format_is_api(self, api_builder: APIPipelineBuilder) -> None:
        assert api_builder.source_format == SourceFormat.API

    def test_api_source_generates_mock_data(self, api_builder: APIPipelineBuilder) -> None:
        pipeline = api_builder.add_source({"endpoint": "/api/users"}).build()
        source_step = next(s for s in pipeline.steps if s.step_type == StepType.SOURCE)
        assert len(source_step.config["sample_data"]) == 20

    def test_api_mock_data_contains_endpoint_field(self, api_builder: APIPipelineBuilder) -> None:
        pipeline = api_builder.add_source({"endpoint": "/api/products"}).build()
        source_step = next(s for s in pipeline.steps if s.step_type == StepType.SOURCE)
        assert source_step.config["sample_data"][0]["endpoint"] == "/api/products"


# ---------------------------------------------------------------------------
# Domain — Pipeline.execute()
# ---------------------------------------------------------------------------

class TestPipelineExecute:
    def test_execute_source_step_returns_data(
        self, sample_rows: list[dict[str, object]]
    ) -> None:
        builder = CSVPipelineBuilder()
        pipeline = builder.add_source({"content": SAMPLE_CSV}).build()
        results = pipeline.execute(sample_rows)
        assert results[0].success
        assert results[0].rows_out == len(sample_rows)

    def test_execute_filter_reduces_rows(
        self, sample_rows: list[dict[str, object]]
    ) -> None:
        builder = CSVPipelineBuilder()
        pipeline = (
            builder
            .add_source({"content": SAMPLE_CSV})
            .add_filter("amount > 100")
            .build()
        )
        results = pipeline.execute(sample_rows)
        filter_result = results[1]
        assert filter_result.success
        # amount > 100 keeps rows with 200, 150, 300, 200 → 4 rows
        assert filter_result.rows_out == 4

    def test_execute_deduplicate_removes_duplicates(
        self, sample_rows: list[dict[str, object]]
    ) -> None:
        builder = CSVPipelineBuilder()
        pipeline = (
            builder
            .add_source({"content": SAMPLE_CSV})
            .add_transform("deduplicate", {})
            .build()
        )
        results = pipeline.execute(sample_rows)
        dedup_result = results[1]
        assert dedup_result.success
        # 5 rows with one duplicate → 4 unique rows
        assert dedup_result.rows_out == 4

    def test_execute_sort_step_succeeds(
        self, sample_rows: list[dict[str, object]]
    ) -> None:
        builder = CSVPipelineBuilder()
        pipeline = (
            builder
            .add_source({"content": SAMPLE_CSV})
            .add_transform("sort", {"column": "name"})
            .build()
        )
        results = pipeline.execute(sample_rows)
        assert all(r.success for r in results)

    def test_execute_rename_transform(
        self, sample_rows: list[dict[str, object]]
    ) -> None:
        builder = CSVPipelineBuilder()
        pipeline = (
            builder
            .add_source({"content": SAMPLE_CSV})
            .add_transform("rename", {"mapping": {"name": "full_name"}})
            .build()
        )
        results = pipeline.execute(sample_rows)
        rename_result = results[1]
        assert rename_result.success
        assert "full_name" in rename_result.preview[0]
        assert "name" not in rename_result.preview[0]


# ---------------------------------------------------------------------------
# ETLDirector
# ---------------------------------------------------------------------------

class TestETLDirector:
    def test_standard_etl_has_four_steps(self) -> None:
        builder = CSVPipelineBuilder()
        director = ETLDirector(builder)
        pipeline = director.build_standard_etl({"content": SAMPLE_CSV})
        assert len(pipeline.steps) == 4

    def test_validation_pipeline_has_filter_step(self) -> None:
        builder = JSONPipelineBuilder()
        director = ETLDirector(builder)
        pipeline = director.build_validation_pipeline(
            {"content": SAMPLE_JSON}, "amount > 100"
        )
        assert any(s.step_type == StepType.FILTER for s in pipeline.steps)

    def test_aggregation_pipeline_has_aggregate_step(self) -> None:
        builder = APIPipelineBuilder()
        director = ETLDirector(builder)
        pipeline = director.build_aggregation_pipeline(
            {"endpoint": "/api/data"}, "category", "value"
        )
        transform_configs = [
            s.config.get("type") for s in pipeline.steps if s.step_type == StepType.TRANSFORM
        ]
        assert "aggregate" in transform_configs

    def test_director_uses_builder_abstraction(self) -> None:
        """Director must accept any PipelineBuilder — not a concrete type."""
        for builder in [CSVPipelineBuilder(), JSONPipelineBuilder(), APIPipelineBuilder()]:
            director = ETLDirector(builder)
            assert isinstance(director, ETLDirector)


# ---------------------------------------------------------------------------
# Step describe()
# ---------------------------------------------------------------------------

class TestPipelineStepDescribe:
    def test_describe_includes_step_type(self) -> None:
        builder = CSVPipelineBuilder()
        pipeline = builder.add_source({"content": SAMPLE_CSV}).build()
        descriptions = pipeline.describe()
        assert any("SOURCE" in d for d in descriptions)
