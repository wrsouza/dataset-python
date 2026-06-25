"""Parses a JSON/YAML task definition file into a BuildTask tree.

Keeping parsing in infrastructure (rather than domain or application) means
the domain stays free of any knowledge of file formats, and the application
use case that builds the tree only depends on the abstract shape of the
parsed data, not on JSON or YAML specifically.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from src.build_tasks.domain.exceptions import TaskDefinitionError
from src.build_tasks.domain.interfaces import BuildTask
from src.build_tasks.infrastructure.leaf_tasks import ShellCommandTask, SimulatedTask
from src.build_tasks.infrastructure.task_group import TaskGroup

SUPPORTED_LEAF_TYPES = {"shell", "simulated"}


def load_definition(path: Path) -> dict[str, Any]:
    """Read a `.json` or `.yml`/`.yaml` file into a plain dict."""
    raw_text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return _parse_json(raw_text)
    if path.suffix in {".yml", ".yaml"}:
        return _parse_yaml(raw_text)
    raise TaskDefinitionError(f"unsupported file extension '{path.suffix}'")


def _parse_json(raw_text: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise TaskDefinitionError(f"invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise TaskDefinitionError("root of definition must be a mapping")
    return parsed


def _parse_yaml(raw_text: str) -> dict[str, Any]:
    try:
        parsed = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise TaskDefinitionError(f"invalid YAML: {exc}") from exc
    if not isinstance(parsed, dict):
        raise TaskDefinitionError("root of definition must be a mapping")
    return parsed


def build_task_tree(definition: dict[str, Any]) -> BuildTask:
    """Recursively build a BuildTask (Leaf or Composite) from a dict node."""
    node_type = definition.get("type")
    name = definition.get("name")
    if not isinstance(name, str) or not name:
        raise TaskDefinitionError("every task node requires a non-empty 'name'")

    if node_type == "group":
        return _build_group(name, definition)
    if node_type in SUPPORTED_LEAF_TYPES:
        return _build_leaf(node_type, name, definition)
    raise TaskDefinitionError(f"unknown task type '{node_type}' for task '{name}'")


def _build_group(name: str, definition: dict[str, Any]) -> TaskGroup:
    stop_on_failure = bool(definition.get("stop_on_failure", True))
    group = TaskGroup(name, stop_on_failure=stop_on_failure)
    children = definition.get("tasks", [])
    if not isinstance(children, list):
        raise TaskDefinitionError(f"group '{name}' must have a list 'tasks'")
    for child_definition in children:
        group.add(build_task_tree(child_definition))
    return group


def _build_leaf(node_type: str, name: str, definition: dict[str, Any]) -> BuildTask:
    if node_type == "shell":
        command = definition.get("command")
        if not isinstance(command, str) or not command:
            raise TaskDefinitionError(f"shell task '{name}' requires a 'command'")
        return ShellCommandTask(name, command)

    duration = float(definition.get("duration_seconds", 0.1))
    should_succeed = bool(definition.get("should_succeed", True))
    return SimulatedTask(name, duration_seconds=duration, should_succeed=should_succeed)
