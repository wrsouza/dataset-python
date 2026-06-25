"""Parses a dashboard definition (dict/JSON) into a DashboardComponent tree.

Keeping parsing in infrastructure (rather than domain or application) means
the domain stays free of any knowledge of dict/JSON shapes, and the
application layer that builds the tree only depends on the abstract
`DashboardComponent`, not on this parsing logic.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.dashboard.domain.exceptions import DashboardDefinitionError
from src.dashboard.domain.interfaces import DashboardComponent
from src.dashboard.infrastructure.containers import Column, Row, TabGroup
from src.dashboard.infrastructure.registry import build_leaf_widget

CONTAINER_BUILDERS: dict[str, type[Row | Column | TabGroup]] = {
    "row": Row,
    "column": Column,
    "tab_group": TabGroup,
}


def load_definition_from_json(raw_text: str) -> dict[str, Any]:
    """Parse a JSON string into a plain dict definition."""
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise DashboardDefinitionError(f"invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise DashboardDefinitionError("root of definition must be a mapping")
    return parsed


def load_definition_from_file(path: Path) -> dict[str, Any]:
    """Read a `.json` dashboard definition file into a plain dict."""
    return load_definition_from_json(path.read_text(encoding="utf-8"))


def build_component_tree(definition: dict[str, Any]) -> DashboardComponent:
    """Recursively build a DashboardComponent (Leaf or Composite) from a dict.

    Expected shape for a leaf:
        {"type": "metric_card", "name": "...", "props": {...}}

    Expected shape for a container:
        {"type": "row", "name": "...", "children": [ ... ]}
    """
    node_type = definition.get("type")
    name = definition.get("name")
    if not isinstance(name, str) or not name:
        raise DashboardDefinitionError("every node requires a non-empty 'name'")
    if not isinstance(node_type, str) or not node_type:
        raise DashboardDefinitionError(f"node '{name}' requires a non-empty 'type'")

    container_cls = CONTAINER_BUILDERS.get(node_type)
    if container_cls is not None:
        return _build_container(container_cls, name, definition)
    return _build_leaf(node_type, name, definition)


def _build_container(
    container_cls: type[Row | Column | TabGroup],
    name: str,
    definition: dict[str, Any],
) -> DashboardComponent:
    container = container_cls(name)
    children = definition.get("children", [])
    if not isinstance(children, list):
        raise DashboardDefinitionError(
            f"container '{name}' must have a list 'children'"
        )
    for child_definition in children:
        container.add(build_component_tree(child_definition))
    return container


def _build_leaf(
    node_type: str, name: str, definition: dict[str, Any]
) -> DashboardComponent:
    props = definition.get("props", {})
    if not isinstance(props, dict):
        raise DashboardDefinitionError(f"leaf '{name}' must have a mapping 'props'")
    return build_leaf_widget(node_type, name, props)
