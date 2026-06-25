"""Unit tests for application use cases, exercised against real leaves."""

from __future__ import annotations

from pathlib import Path

from src.build_tasks.application.use_cases import (
    BuildTaskTreeFromFileUseCase,
    ExecuteBuildTaskUseCase,
)
from src.build_tasks.domain.entities import TaskStatus
from src.build_tasks.infrastructure.leaf_tasks import SimulatedTask
from src.build_tasks.infrastructure.task_group import TaskGroup


class TestBuildTaskTreeFromFileUseCase:
    def test_builds_tree_from_example_file(self, example_definition_path: Path) -> None:
        task = BuildTaskTreeFromFileUseCase().execute(example_definition_path)

        assert task.name == "build_all"


class TestExecuteBuildTaskUseCase:
    def test_summarizes_successful_tree(self) -> None:
        group = TaskGroup("build_all")
        group.add(SimulatedTask("compile", should_succeed=True))
        group.add(SimulatedTask("package", should_succeed=True))

        summary = ExecuteBuildTaskUseCase().execute(group)

        assert summary.overall_status == TaskStatus.SUCCESS
        assert summary.tasks_succeeded == 2
        assert summary.tasks_failed == 0

    def test_summarizes_tree_with_failures(self) -> None:
        group = TaskGroup("build_all", stop_on_failure=False)
        group.add(SimulatedTask("compile", should_succeed=False))
        group.add(SimulatedTask("package", should_succeed=True))

        summary = ExecuteBuildTaskUseCase().execute(group)

        assert summary.overall_status == TaskStatus.FAILURE
        assert summary.tasks_succeeded == 1
        assert summary.tasks_failed == 1

    def test_summarizes_single_leaf_task(self) -> None:
        leaf = SimulatedTask("compile", should_succeed=True)

        summary = ExecuteBuildTaskUseCase().execute(leaf)

        assert summary.tasks_succeeded == 1
        assert summary.tasks_failed == 0
