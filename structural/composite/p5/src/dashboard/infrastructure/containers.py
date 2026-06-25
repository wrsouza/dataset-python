"""The Composite implementations of `DashboardComponent`.

`Row`, `Column` and `TabGroup` each hold an ordered list of child
`DashboardComponent`s — which may themselves be containers, allowing
arbitrarily nested dashboard layouts (a `TabGroup` containing `Row`s that
contain `Column`s that contain charts). Every container is fully
substitutable for `DashboardComponent` (Liskov Substitution): client code
that calls `component.render()` cannot tell, and does not need to tell,
whether `component` is a single widget or a deeply nested container.
"""

from __future__ import annotations

from typing import Any

from src.dashboard.domain.exceptions import DuplicateChildComponentError
from src.dashboard.domain.interfaces import DashboardComponent


class _BaseContainer(DashboardComponent):
    """Shared behavior for layout containers (SRP: only child management).

    Concrete containers only need to provide `component_type` and the
    `layout` metadata that distinguishes how their children are arranged;
    child storage, counting and depth calculation live here once.
    """

    def __init__(self, name: str) -> None:
        self._name = name
        self._children: list[DashboardComponent] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def children(self) -> tuple[DashboardComponent, ...]:
        """Return the child components in layout order."""
        return tuple(self._children)

    def add(self, component: DashboardComponent) -> None:
        """Append a child component, rejecting duplicate names at this level."""
        if any(child.name == component.name for child in self._children):
            raise DuplicateChildComponentError(self._name, component.name)
        self._children.append(component)

    def count_widgets(self) -> int:
        return sum(child.count_widgets() for child in self._children)

    def depth(self) -> int:
        if not self._children:
            return 1
        return 1 + max(child.depth() for child in self._children)

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "name": self._name,
            "children": [child.render() for child in self._children],
        }


class Row(_BaseContainer):
    """Composite: arranges children horizontally, side by side."""

    component_type_name = "row"

    @property
    def component_type(self) -> str:
        return self.component_type_name


class Column(_BaseContainer):
    """Composite: arranges children vertically, stacked."""

    component_type_name = "column"

    @property
    def component_type(self) -> str:
        return self.component_type_name


class TabGroup(_BaseContainer):
    """Composite: arranges children as a set of selectable tabs."""

    component_type_name = "tab_group"

    @property
    def component_type(self) -> str:
        return self.component_type_name

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["tab_labels"] = [child.name for child in self._children]
        return base
