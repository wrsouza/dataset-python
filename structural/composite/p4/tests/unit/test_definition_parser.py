"""Unit tests for parsing task definition files into a BuildTask tree."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.build_tasks.domain.exceptions import TaskDefinitionError
from src.build_tasks.infrastructure.definition_parser import (
    build_task_tree,
    load_definition,
)
from src.build_tasks.infrastructure.leaf_tasks import ShellCommandTask, SimulatedTask
from src.build_tasks.infrastructure.task_group import TaskGroup


class TestLoadDefinition:
    def test_loads_yaml_file(self, example_definition_path: Path) -> None:
        definition = load_definition(example_definition_path)

        assert definition["name"] == "build_all"

    def test_loads_json_file(self, tmp_path: Path) -> None:
        json_path = tmp_path / "tasks.json"
        json_path.write_text('{"type": "simulated", "name": "compile"}')

        definition = load_definition(json_path)

        assert definition["name"] == "compile"

    def test_unsupported_extension_raises(self, tmp_path: Path) -> None:
        bad_path = tmp_path / "tasks.txt"
        bad_path.write_text("irrelevant")

        with pytest.raises(TaskDefinitionError):
            load_definition(bad_path)

    def test_invalid_json_raises(self, tmp_path: Path) -> None:
        bad_path = tmp_path / "tasks.json"
        bad_path.write_text("{not valid json")

        with pytest.raises(TaskDefinitionError):
            load_definition(bad_path)

    def test_invalid_yaml_root_raises(self, tmp_path: Path) -> None:
        bad_path = tmp_path / "tasks.yml"
        bad_path.write_text("- just\n- a\n- list\n")

        with pytest.raises(TaskDefinitionError):
            load_definition(bad_path)


class TestBuildTaskTree:
    def test_builds_simulated_leaf(self) -> None:
        task = build_task_tree({"type": "simulated", "name": "compile"})

        assert isinstance(task, SimulatedTask)
        assert task.name == "compile"

    def test_builds_shell_leaf(self) -> None:
        task = build_task_tree({"type": "shell", "name": "build", "command": "echo hi"})

        assert isinstance(task, ShellCommandTask)

    def test_builds_nested_group_from_example_file(
        self, example_definition_path: Path
    ) -> None:
        definition = load_definition(example_definition_path)
        task = build_task_tree(definition)

        assert isinstance(task, TaskGroup)
        assert task.name == "build_all"
        nested = [child for child in task.children if child.name == "test_all"]
        assert isinstance(nested[0], TaskGroup)
        assert len(nested[0].children) == 2

    def test_missing_name_raises(self) -> None:
        with pytest.raises(TaskDefinitionError):
            build_task_tree({"type": "simulated"})

    def test_unknown_type_raises(self) -> None:
        with pytest.raises(TaskDefinitionError):
            build_task_tree({"type": "mystery", "name": "x"})

    def test_shell_leaf_without_command_raises(self) -> None:
        with pytest.raises(TaskDefinitionError):
            build_task_tree({"type": "shell", "name": "build"})

    def test_group_without_tasks_list_raises(self) -> None:
        with pytest.raises(TaskDefinitionError):
            build_task_tree({"type": "group", "name": "build_all", "tasks": "nope"})
