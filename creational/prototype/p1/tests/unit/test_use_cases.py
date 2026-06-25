"""Unit tests for application use cases using in-memory fakes."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from characters.application.use_cases import (
    CloneCharacterUseCase,
    ListCharactersUseCase,
    ListTemplatesUseCase,
    UpdateCharacterUseCase,
)
from characters.domain.entities import (
    CharacterNotFoundError,
    CharacterRecord,
    CharacterUpdateRequest,
    CloneRequest,
    TemplateNotFoundError,
)
from characters.infrastructure.prototypes import build_default_registry


def make_record(id: int = 1, name: str = "Hero") -> CharacterRecord:
    return CharacterRecord(
        id=id,
        name=name,
        template_name="warrior",
        stats_json={"strength": 18},
        created_at=datetime.utcnow(),
    )


class TestListTemplatesUseCase:
    def test_returns_template_names(self) -> None:
        registry = build_default_registry()
        use_case = ListTemplatesUseCase(registry)
        result = use_case.execute()
        assert "warrior" in result
        assert "mage" in result
        assert "rogue" in result


class TestCloneCharacterUseCase:
    @pytest.mark.asyncio
    async def test_clone_persists_record(self) -> None:
        registry = build_default_registry()
        repo = AsyncMock()
        repo.save.return_value = make_record(id=1, name="Warrior Clone")

        use_case = CloneCharacterUseCase(registry, repo)
        request = CloneRequest(character_name="warrior", overrides={"name": "My Hero"})
        result = await use_case.execute(request)

        repo.save.assert_called_once()
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_clone_unknown_template_raises(self) -> None:
        registry = build_default_registry()
        repo = AsyncMock()
        use_case = CloneCharacterUseCase(registry, repo)
        request = CloneRequest(character_name="paladin", overrides={})
        with pytest.raises(TemplateNotFoundError):
            await use_case.execute(request)


class TestListCharactersUseCase:
    @pytest.mark.asyncio
    async def test_returns_all_records(self) -> None:
        repo = AsyncMock()
        repo.find_all.return_value = [make_record(1), make_record(2)]
        use_case = ListCharactersUseCase(repo)
        result = await use_case.execute()
        assert len(result) == 2


class TestUpdateCharacterUseCase:
    @pytest.mark.asyncio
    async def test_update_returns_updated_record(self) -> None:
        repo = AsyncMock()
        repo.update.return_value = make_record(1, "Updated Hero")
        use_case = UpdateCharacterUseCase(repo)
        result = await use_case.execute(1, CharacterUpdateRequest(name="Updated Hero"))
        assert result.name == "Updated Hero"

    @pytest.mark.asyncio
    async def test_update_not_found_raises(self) -> None:
        repo = AsyncMock()
        repo.update.return_value = None
        use_case = UpdateCharacterUseCase(repo)
        with pytest.raises(CharacterNotFoundError):
            await use_case.execute(999, CharacterUpdateRequest(name="Ghost"))
