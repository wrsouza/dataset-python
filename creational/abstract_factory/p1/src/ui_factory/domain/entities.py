"""Domain entities and value objects for the UI Component Factory.

These dataclasses represent the data structures returned by rendered components
and stored as usage logs in PostgreSQL.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ComponentProperties:
    """Value object representing the rendered properties of any UI component."""

    component_type: str
    platform: str
    style: str
    properties: dict[str, str]


@dataclass
class ComponentUsageLog:
    """Entity representing a log entry stored in PostgreSQL.

    Tracks which platform/component combinations are requested via the API.
    """

    platform: str
    component_family: list[str]
    requested_at: datetime = field(default_factory=datetime.utcnow)
    id: int | None = None

    def to_dict(self) -> dict[str, object]:
        """Serialize log entry to a plain dictionary for JSON responses."""
        return {
            "id": self.id,
            "platform": self.platform,
            "component_family": self.component_family,
            "requested_at": self.requested_at.isoformat(),
        }


@dataclass(frozen=True)
class ComponentFamilyResponse:
    """Value object representing the full rendered family for an API response."""

    platform: str
    button: dict[str, str]
    input: dict[str, str]
    modal: dict[str, str]

    def to_dict(self) -> dict[str, object]:
        """Serialize the entire family response to a plain dictionary."""
        return {
            "platform": self.platform,
            "components": {
                "button": self.button,
                "input": self.input,
                "modal": self.modal,
            },
        }
