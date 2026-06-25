"""Integration tests for Pipeline Builder — full pipeline execution flows."""
from __future__ import annotations

from pipeline_builder.application.use_cases import BuildPipelineUseCase, ETLDirector
from pipeline_builder.domain.entities import ExecutionResult, SourceFormat
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

SAMPLE_ROWS = [
    {"id": "1", "name": "Alice", "category": "A", "amount": "100"},
    {"id": "2", "name": "Bob", "category": "B", "amount": "200"},
    {"id": "3", "name": "Alice", "category": "A", "amount": "150"},
    {"id": "4", "name": "Carol", "category": "C", "amount": "300"},
    {"id": "2", "name": "Bob", "category": "B", "amount": "200"},
]


class TestFullCSVETLPipeline:
    """End-to-end: CSV source → deduplicate → sort → sink."""

    def test_standard_etl_executes_all_steps_successfully(self) -> None:
        builder = CSVPipelineBuilder()
        director = ETLDirector(builder)
        pipeline = director.build_standard_etl({"content": SAMPLE_CSV})

        results: list[ExecutionResult] = pipeline.execute(SAMPLE_ROWS)

        assert len(results) == 4
        assert all(r.success for r in results), [r.summary for r in results]

    def test_standard_etl_deduplicates_before_sink(self) -> None:
        builder = CSVPipelineBuilder()
        director = ETLDirector(builder)
        pipeline = director.build_standard_etl({"content": SAMPLE_CSV})

        results = pipeline.execute(SAMPLE_ROWS)

        # step index 1 is deduplicate
        dedup_result = results[1]
        assert dedup_result.rows_out < dedup_result.rows_in

    def test_validation_pipeline_filters_correctly(self) -> None:
        builder = CSVPipelineBuilder()
        director = ETLDirector(builder)
        pipeline = director.build_validation_pipeline({"content": SAMPLE_CSV}, "amount > 150")

        results = pipeline.execute(SAMPLE_ROWS)

        filter_result = next(r for r in results if "filter" in r.step_name)
        assert filter_result.success
        # Rows with amount > 150: Bob(200), Carol(300), Bob(200) → 3
        assert filter_result.rows_out == 3


class TestBuildPipelineUseCase:
    """Test use-case accepts step dicts and builds + executes the pipeline."""

    def test_use_case_builds_pipeline_from_spec(self) -> None:
        steps = [
            {"type": "source", "config": {"content": SAMPLE_CSV, "format": "csv"}},
            {"type": "transform", "config": {"transform_type": "sort", "column": "name"}},
            {"type": "sink", "config": {"destination": "console"}},
        ]
        use_case = BuildPipelineUseCase(CSVPipelineBuilder())
        pipeline = use_case.execute(steps)

        results = pipeline.execute(SAMPLE_ROWS)
        assert all(r.success for r in results)

    def test_use_case_with_filter_step(self) -> None:
        steps = [
            {"type": "source", "config": {"content": SAMPLE_CSV, "format": "csv"}},
            {"type": "filter", "config": {"condition": "name == Alice"}},
            {"type": "sink", "config": {"destination": "report"}},
        ]
        use_case = BuildPipelineUseCase(CSVPipelineBuilder())
        pipeline = use_case.execute(steps)

        results = pipeline.execute(SAMPLE_ROWS)
        filter_result = results[1]
        assert filter_result.rows_out == 2  # Alice appears twice


class TestAPIAndJSONPipelines:
    def test_api_pipeline_generates_mock_data(self) -> None:
        builder = APIPipelineBuilder()
        director = ETLDirector(builder)
        pipeline = director.build_standard_etl({"endpoint": "/api/items"})

        source_step = pipeline.steps[0]
        mock_data: list[dict[str, object]] = source_step.config.get("sample_data", [])
        results = pipeline.execute(mock_data)

        assert results[0].success
        assert results[0].rows_in == 20

    def test_json_aggregation_pipeline(self) -> None:
        json_rows = [
            {"id": 1, "category": "A", "amount": 100},
            {"id": 2, "category": "B", "amount": 200},
            {"id": 3, "category": "A", "amount": 150},
        ]
        builder = JSONPipelineBuilder()
        director = ETLDirector(builder)
        pipeline = director.build_aggregation_pipeline(
            {"content": "[]"}, "category", "amount"
        )
        results = pipeline.execute(json_rows)

        agg_result = next((r for r in results if "aggregate" in r.step_name), None)
        assert agg_result is not None
        assert agg_result.success
        # Two unique categories: A and B
        assert agg_result.rows_out == 2


class TestExecutionResultSummary:
    def test_success_summary_format(self) -> None:
        result = ExecutionResult(
            step_name="source_1", success=True, rows_in=5, rows_out=5
        )
        assert "OK" in result.summary
        assert "5" in result.summary

    def test_failure_summary_format(self) -> None:
        result = ExecutionResult(
            step_name="filter_2",
            success=False,
            error="Column not found",
        )
        assert "FAILED" in result.summary
        assert "Column not found" in result.summary
