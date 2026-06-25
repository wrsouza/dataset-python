"""Unit tests for TaskResult and ExecutionSummary aggregation logic."""

from __future__ import annotations

from src.build_tasks.domain.entities import ExecutionSummary, TaskResult, TaskStatus


class TestTaskResult:
    def test_leaf_result_is_success_when_status_success(self) -> None:
        result = TaskResult("compile", TaskStatus.SUCCESS, 0.1)

        assert result.is_success is True

    def test_leaf_result_is_not_success_when_status_failure(self) -> None:
        result = TaskResult("compile", TaskStatus.FAILURE, 0.1)

        assert result.is_success is False

    def test_count_leaf_results_for_plain_leaf(self) -> None:
        result = TaskResult("compile", TaskStatus.SUCCESS, 0.1)

        assert result.count_leaf_results() == (1, 0)

    def test_count_leaf_results_aggregates_nested_children(self) -> None:
        child_a = TaskResult("unit_tests", TaskStatus.SUCCESS, 0.1)
        child_b = TaskResult("integration_tests", TaskStatus.FAILURE, 0.2)
        nested_group = TaskResult(
            "test_all", TaskStatus.FAILURE, 0.3, children_results=(child_a, child_b)
        )
        root = TaskResult(
            "build_all", TaskStatus.FAILURE, 0.4, children_results=(nested_group,)
        )

        assert root.count_leaf_results() == (1, 1)


class TestExecutionSummary:
    def test_overall_status_is_success_when_no_failures(self) -> None:
        summary = ExecutionSummary(
            root_result=TaskResult("build_all", TaskStatus.SUCCESS, 1.0),
            total_duration_seconds=1.0,
            tasks_succeeded=3,
            tasks_failed=0,
        )

        assert summary.overall_status == TaskStatus.SUCCESS

    def test_overall_status_is_failure_when_any_failure(self) -> None:
        summary = ExecutionSummary(
            root_result=TaskResult("build_all", TaskStatus.FAILURE, 1.0),
            total_duration_seconds=1.0,
            tasks_succeeded=2,
            tasks_failed=1,
        )

        assert summary.overall_status == TaskStatus.FAILURE
