"""Domain entities for the dashboard config system."""

from __future__ import annotations

from dataclasses import dataclass, field


class TemplateNotFoundError(Exception):
    """Raised when a requested template does not exist in the registry."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Dashboard template '{name}' not found in registry")


@dataclass
class CloneRequest:
    """Request data for cloning a dashboard config template."""

    template_name: str
    overrides: dict[str, object] = field(default_factory=dict)
    new_title: str = ""
