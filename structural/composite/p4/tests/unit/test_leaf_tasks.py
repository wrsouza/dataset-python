"""Unit tests for Leaf BuildTask implementations, isolated from the tree."""

from __future__ import annotations

import pytest

from src.build_tasks.domain.entities import TaskStatus
from src.build_tasks.domain.exceptions import TaskExecutionError
from src.build_tasks.infrastructure.leaf_tasks import (
    PythonFunctionTask,
    ShellCommandTask,
    SimulatedTask,
)


class TestSimulatedTask:
    def test_reports_success_when_configured_to_succeed(self) -> None:
        task = SimulatedTask("compile", should_succeed=True)

        result = task.execute()

        assert result.status == TaskStatus.SUCCESS
        assert result.task_name == "compile"

    def test_reports_failure_when_configured_to_fail(self) -> None:
        task = SimulatedTask("compile", should_succeed=False)

        result = task.execute()

        assert result.status == TaskStatus.FAILURE

    def test_estimated_duration_matches_constructor_argument(self) -> None:
        task = SimulatedTask("compile", duration_seconds=2.5)

        assert task.estimated_duration_seconds() == 2.5

    def test_name_property_returns_constructor_value(self) -> None:
        task = SimulatedTask("compile")

        assert task.name == "compile"


class TestShellCommandTask:
    def test_successful_command_yields_success_result(self) -> None:
        task = ShellCommandTask("echo_hello", "echo hello")

        result = task.execute()

        assert result.status == TaskStatus.SUCCESS
        assert "hello" in result.message

    def test_failing_command_yields_failure_result(self) -> None:
        task = ShellCommandTask("fail", "exit 1")

        result = task.execute()

        assert result.status == TaskStatus.FAILURE

    def test_estimated_duration_is_a_positive_number(self) -> None:
        task = ShellCommandTask("noop", "echo noop")

        assert task.estimated_duration_seconds() > 0

    def test_timeout_raises_task_execution_error(self) -> None:
        task = ShellCommandTask("slow", "echo start")
        task._command = 'python -c "import time; time.sleep(120)"'  # noqa: SLF001

        with pytest.raises(TaskExecutionError):
            task.execute()


class TestPythonFunctionTask:
    def test_successful_callable_yields_success_result(self) -> None:
        calls: list[str] = []
        task = PythonFunctionTask("record", lambda: calls.append("ran"))

        result = task.execute()

        assert result.status == TaskStatus.SUCCESS
        assert calls == ["ran"]

    def test_raising_callable_yields_failure_result_with_message(self) -> None:
        def _boom() -> None:
            raise ValueError("kaboom")

        task = PythonFunctionTask("boom", _boom)

        result = task.execute()

        assert result.status == TaskStatus.FAILURE
        assert "kaboom" in result.message
