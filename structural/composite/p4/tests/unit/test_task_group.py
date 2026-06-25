"""Unit tests for TaskGroup: the Composite node, including nested groups."""

from __future__ import annotations

import pytest

from src.build_tasks.domain.entities import TaskStatus
from src.build_tasks.domain.exceptions import DuplicateChildTaskError
from src.build_tasks.infrastructure.leaf_tasks import SimulatedTask
from src.build_tasks.infrastructure.task_group import TaskGroup


class TestTaskGroupWithLeavesOnly:
    def test_all_children_succeeding_yields_success(self) -> None:
        group = TaskGroup("build_all")
        group.add(SimulatedTask("compile", should_succeed=True))
        group.add(SimulatedTask("package", should_succeed=True))

        result = group.execute()

        assert result.status == TaskStatus.SUCCESS
        assert len(result.children_results) == 2

    def test_one_failing_child_propagates_failure_to_group(self) -> None:
        group = TaskGroup("build_all")
        group.add(SimulatedTask("compile", should_succeed=False))
        group.add(SimulatedTask("package", should_succeed=True))

        result = group.execute()

        assert result.status == TaskStatus.FAILURE

    def test_stop_on_failure_skips_remaining_children(self) -> None:
        group = TaskGroup("build_all", stop_on_failure=True)
        group.add(SimulatedTask("compile", should_succeed=False))
        group.add(SimulatedTask("package", should_succeed=True))

        result = group.execute()

        assert len(result.children_results) == 1

    def test_stop_on_failure_false_runs_all_children(self) -> None:
        group = TaskGroup("test_all", stop_on_failure=False)
        group.add(SimulatedTask("unit_tests", should_succeed=False))
        group.add(SimulatedTask("integration_tests", should_succeed=True))

        result = group.execute()

        assert len(result.children_results) == 2
        assert result.status == TaskStatus.FAILURE

    def test_adding_duplicate_child_name_raises(self) -> None:
        group = TaskGroup("build_all")
        group.add(SimulatedTask("compile"))

        with pytest.raises(DuplicateChildTaskError):
            group.add(SimulatedTask("compile"))

    def test_estimated_duration_sums_children(self) -> None:
        group = TaskGroup("build_all")
        group.add(SimulatedTask("compile", duration_seconds=1.0))
        group.add(SimulatedTask("package", duration_seconds=2.0))

        assert group.estimated_duration_seconds() == 3.0

    def test_children_property_preserves_insertion_order(self) -> None:
        group = TaskGroup("build_all")
        group.add(SimulatedTask("compile"))
        group.add(SimulatedTask("package"))

        names = [child.name for child in group.children]

        assert names == ["compile", "package"]


class TestNestedTaskGroups:
    def test_composite_inside_composite_executes_recursively(self) -> None:
        test_all = TaskGroup("test_all")
        test_all.add(SimulatedTask("unit_tests", should_succeed=True))
        test_all.add(SimulatedTask("integration_tests", should_succeed=True))

        build_all = TaskGroup("build_all")
        build_all.add(SimulatedTask("compile", should_succeed=True))
        build_all.add(test_all)
        build_all.add(SimulatedTask("package", should_succeed=True))

        result = build_all.execute()

        assert result.status == TaskStatus.SUCCESS
        assert len(result.children_results) == 3
        nested_result = result.children_results[1]
        assert nested_result.task_name == "test_all"
        assert len(nested_result.children_results) == 2

    def test_failure_in_nested_group_propagates_to_root(self) -> None:
        test_all = TaskGroup("test_all", stop_on_failure=False)
        test_all.add(SimulatedTask("unit_tests", should_succeed=True))
        test_all.add(SimulatedTask("integration_tests", should_succeed=False))

        build_all = TaskGroup("build_all", stop_on_failure=False)
        build_all.add(SimulatedTask("compile", should_succeed=True))
        build_all.add(test_all)
        build_all.add(SimulatedTask("package", should_succeed=True))

        result = build_all.execute()

        assert result.status == TaskStatus.FAILURE
        succeeded, failed = result.count_leaf_results()
        assert succeeded == 3
        assert failed == 1

    def test_client_treats_leaf_and_composite_identically(self) -> None:
        leaf = SimulatedTask("compile")
        group = TaskGroup("build_all")
        group.add(SimulatedTask("compile"))

        for task in (leaf, group):
            result = task.execute()
            assert result.task_name == task.name
            assert hasattr(task, "execute")
            assert hasattr(task, "estimated_duration_seconds")
