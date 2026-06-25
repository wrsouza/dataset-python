"""Entities and value objects for the dashboard component domain.

These dataclasses hold the data each Leaf widget carries. Keeping the data
shape separate from the `DashboardComponent` behavior (render/count/depth)
follows SRP: entities describe *what* a widget is, while the infrastructure
classes describe *how* it behaves in the tree.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MetricCardData:
    """Data for a single KPI metric card widget."""

    label: str
    value: str
    delta: str | None = None


@dataclass(frozen=True)
class TextBlockData:
    """Data for a block of free-form text or markdown."""

    content: str
    markdown: bool = True


@dataclass(frozen=True)
class ChartData:
    """Data for a chart widget.

    `series` maps series name to a list of numeric points, kept generic on
    purpose: the domain does not care which charting library eventually
    draws it.
    """

    chart_type: str
    series: dict[str, list[float]] = field(default_factory=dict)
    x_labels: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class TreeMetrics:
    """Aggregated metrics computed over a dashboard component tree."""

    widget_count: int
    depth: int
    container_count: int
