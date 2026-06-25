"""The Component interface of the Composite pattern.

`DashboardComponent` is implemented both by atomic Leaf widgets (e.g. a
metric card or a chart) and by composite layout containers (`Row`,
`Column`, `TabGroup`) that hold other `DashboardComponent`s, including other
containers. Client code (the application layer, the Streamlit app) only
ever talks to this interface, so it never needs to branch on "is this a
widget or a container?" — that transparency is the whole point of the
pattern.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DashboardComponent(ABC):
    """Component: anything that can be rendered and serialized.

    Both Leaf widgets and Composite containers implement this same
    interface (Liskov Substitution): wherever a `DashboardComponent` is
    expected, a single metric card or a deeply nested tab group works the
    same way.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the human-readable identifier of this component."""

    @property
    @abstractmethod
    def component_type(self) -> str:
        """Return the concrete type discriminator (e.g. 'metric_card')."""

    @abstractmethod
    def render(self) -> dict[str, Any]:
        """Return a JSON-serializable structure describing how to render.

        For a Leaf this is the widget's own data; for a Composite it also
        includes the rendered representation of every child, recursively.
        The real UI layer (Streamlit) turns this structured data into
        `st.*` calls — no rendering logic leaks into the domain.
        """

    @abstractmethod
    def count_widgets(self) -> int:
        """Return how many Leaf widgets exist in this subtree."""

    @abstractmethod
    def depth(self) -> int:
        """Return the depth of this subtree (a Leaf has depth 1)."""
