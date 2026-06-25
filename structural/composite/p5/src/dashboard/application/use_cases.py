"""Use cases orchestrating the dashboard component domain.

These classes depend only on the abstract `DashboardComponent` interface
(Dependency Inversion): they have no idea whether a given node is a
`MetricCard`, a `ChartWidget`, or a `TabGroup` containing dozens of nested
children.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.dashboard.domain.entities import TreeMetrics
from src.dashboard.domain.interfaces import DashboardComponent
from src.dashboard.infrastructure.definition_parser import (
    build_component_tree,
    load_definition_from_file,
    load_definition_from_json,
)


class BuildDashboardTreeUseCase:
    """Builds a DashboardComponent tree from a dict definition."""

    def execute(self, definition: dict[str, Any]) -> DashboardComponent:
        """Parse `definition` and return its root DashboardComponent."""
        return build_component_tree(definition)


class BuildDashboardTreeFromJsonUseCase:
    """Builds a DashboardComponent tree from a raw JSON string."""

    def execute(self, raw_json: str) -> DashboardComponent:
        """Parse `raw_json` and return its root DashboardComponent."""
        definition = load_definition_from_json(raw_json)
        return build_component_tree(definition)


class BuildDashboardTreeFromFileUseCase:
    """Builds a DashboardComponent tree from a JSON definition file."""

    def execute(self, definition_path: Path) -> DashboardComponent:
        """Parse `definition_path` and return its root DashboardComponent."""
        definition = load_definition_from_file(definition_path)
        return build_component_tree(definition)


class RenderDashboardUseCase:
    """Extracts the renderable, JSON-serializable shape of a tree."""

    def execute(self, component: DashboardComponent) -> dict[str, Any]:
        """Return the structured render data for `component` and children.

        The result contains no Streamlit (or any UI library) calls — only
        plain dicts/lists — so it can be tested without a UI and consumed
        by `app.py` to drive `st.*` calls.
        """
        return component.render()


class ComputeTreeMetricsUseCase:
    """Computes aggregated metrics (widget count, depth) for a tree."""

    def execute(self, component: DashboardComponent) -> TreeMetrics:
        """Return widget/container counts and the maximum depth of the tree."""
        widget_count = component.count_widgets()
        depth = component.depth()
        container_count = _count_containers(component)
        return TreeMetrics(
            widget_count=widget_count,
            depth=depth,
            container_count=container_count,
        )


def _count_containers(component: DashboardComponent) -> int:
    """Count container nodes by walking the rendered tree structure.

    Walking `render()` output (rather than requiring an extra interface
    method) keeps `DashboardComponent` focused on rendering and counting
    widgets only (Interface Segregation) — this is purely an application
    concern derived from the public `render()` contract.
    """
    rendered = component.render()
    children = rendered.get("children")
    if not isinstance(children, list):
        return 0
    total = 1
    for child in children:
        total += _count_containers_from_render(child)
    return total


def _count_containers_from_render(rendered: dict[str, Any]) -> int:
    children = rendered.get("children")
    if not isinstance(children, list):
        return 0
    total = 1
    for child in children:
        total += _count_containers_from_render(child)
    return total
