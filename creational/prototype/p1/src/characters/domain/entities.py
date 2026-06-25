"""Domain entities for the character system."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CharacterRecord:
    """Persisted character record from the database."""

    id: int
    name: str
    template_name: str
    stats_json: dict[str, int]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CloneRequest:
    """Request data for cloning a character template."""

    character_name: str
    overrides: dict[str, object] = field(default_factory=dict)


@dataclass
class CharacterUpdateRequest:
    """Request data for updating a character record."""

    name: str | None = None
    stats: dict[str, int] | None = None
    skills: list[str] | None = None
    equipment: list[str] | None = None
    level: int | None = None


class TemplateNotFoundError(Exception):
    """Raised when a requested template does not exist in the registry."""

    def __init__(self, template_name: str) -> None:
        self.template_name = template_name
        super().__init__(f"Template '{template_name}' not found in registry")


class CharacterNotFoundError(Exception):
    """Raised when a character record is not found."""

    def __init__(self, character_id: int) -> None:
        self.character_id = character_id
        super().__init__(f"Character with id={character_id} not found")
