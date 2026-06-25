"""Leaf implementations of `DashboardComponent`.

Each leaf wraps one concrete kind of atomic widget data (metric card, text
block, chart). Adding a new widget type means writing a new class here and
registering it in `registry.py` — `Row`, `Column` and `TabGroup` never need
to change. This is the Open/Closed Principle in action.
"""

from __future__ import annotations

from typing import Any

from src.dashboard.domain.entities import ChartData, MetricCardData, TextBlockData
from src.dashboard.domain.interfaces import DashboardComponent

LEAF_DEPTH = 1


class MetricCard(DashboardComponent):
    """Leaf widget rendering a single KPI metric."""

    component_type_name = "metric_card"

    def __init__(self, name: str, data: MetricCardData) -> None:
        self._name = name
        self._data = data

    @property
    def name(self) -> str:
        return self._name

    @property
    def component_type(self) -> str:
        return self.component_type_name

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "name": self._name,
            "label": self._data.label,
            "value": self._data.value,
            "delta": self._data.delta,
        }

    def count_widgets(self) -> int:
        return 1

    def depth(self) -> int:
        return LEAF_DEPTH


class TextBlock(DashboardComponent):
    """Leaf widget rendering a block of text or markdown."""

    component_type_name = "text_block"

    def __init__(self, name: str, data: TextBlockData) -> None:
        self._name = name
        self._data = data

    @property
    def name(self) -> str:
        return self._name

    @property
    def component_type(self) -> str:
        return self.component_type_name

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "name": self._name,
            "content": self._data.content,
            "markdown": self._data.markdown,
        }

    def count_widgets(self) -> int:
        return 1

    def depth(self) -> int:
        return LEAF_DEPTH


class ChartWidget(DashboardComponent):
    """Leaf widget rendering a chart over one or more numeric series."""

    component_type_name = "chart"

    def __init__(self, name: str, data: ChartData) -> None:
        self._name = name
        self._data = data

    @property
    def name(self) -> str:
        return self._name

    @property
    def component_type(self) -> str:
        return self.component_type_name

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "name": self._name,
            "chart_type": self._data.chart_type,
            "series": dict(self._data.series),
            "x_labels": list(self._data.x_labels),
        }

    def count_widgets(self) -> int:
        return 1

    def depth(self) -> int:
        return LEAF_DEPTH
