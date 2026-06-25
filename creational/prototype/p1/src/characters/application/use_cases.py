"""Application use cases for the character system.

Each use case has a single responsibility and depends on abstractions (DIP).
"""
from __future__ import annotations

from typing import Any

from characters.domain.entities import (
    CharacterNotFoundError,
    CharacterRecord,
    CharacterUpdateRequest,
    CloneRequest,
    TemplateNotFoundError,
)
from characters.domain.interfaces import CharacterRegistry
from characters.infrastructure.database import CharacterRepository
from characters.infrastructure.prototypes import BaseCharacter


class RegisterTemplateUseCase:
    """Register a new character prototype template.

    SRP: only handles template registration logic.
    """

    def __init__(self, registry: CharacterRegistry) -> None:
        self._registry = registry

    def execute(self, name: str, template: BaseCharacter) -> dict[str, Any]:
        """Register the template and return its serialized form."""
        self._registry.register(name, template)
        return {"registered": name, "templates": self._registry.list_templates()}


class CloneCharacterUseCase:
    """Clone a character template and persist the result.

    SRP: orchestrates clone + persist, nothing more.
    DIP: depends on CharacterRegistry and CharacterRepository abstractions.
    """

    def __init__(
        self,
        registry: CharacterRegistry,
        repository: CharacterRepository,
    ) -> None:
        self._registry = registry
        self._repository = repository

    async def execute(self, request: CloneRequest) -> CharacterRecord:
        """Clone the named template, apply overrides, persist to database."""
        cloned = self._registry.clone(
            name=request.character_name,
            overrides=request.overrides,
        )
        # cloned is a BaseCharacter; we persist its snapshot
        char = cloned  # type: ignore[assignment]
        record = CharacterRecord(
            id=0,
            name=char.name,  # type: ignore[attr-defined]
            template_name=char.template_name,  # type: ignore[attr-defined]
            stats_json=char.stats,  # type: ignore[attr-defined]
        )
        return await self._repository.save(record)


class ListCharactersUseCase:
    """Retrieve all persisted characters.

    SRP: only responsible for listing, no mutation.
    """

    def __init__(self, repository: CharacterRepository) -> None:
        self._repository = repository

    async def execute(self) -> list[CharacterRecord]:
        """Return all characters from the repository."""
        return await self._repository.find_all()


class UpdateCharacterUseCase:
    """Update an existing character record.

    SRP: only handles character mutation logic.
    """

    def __init__(self, repository: CharacterRepository) -> None:
        self._repository = repository

    async def execute(
        self, character_id: int, request: CharacterUpdateRequest
    ) -> CharacterRecord:
        """Apply updates to the character and return the updated record."""
        updates: dict[str, Any] = {}
        if request.name is not None:
            updates["name"] = request.name
        if request.stats is not None:
            updates["stats_json"] = request.stats

        updated = await self._repository.update(character_id, updates)
        if updated is None:
            raise CharacterNotFoundError(character_id)
        return updated


class ListTemplatesUseCase:
    """List all available character templates in the registry."""

    def __init__(self, registry: CharacterRegistry) -> None:
        self._registry = registry

    def execute(self) -> list[str]:
        """Return all registered template names."""
        return self._registry.list_templates()
