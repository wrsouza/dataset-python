"""FastAPI application entry point for the Character Template System."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from characters.application.use_cases import (
    CloneCharacterUseCase,
    ListCharactersUseCase,
    ListTemplatesUseCase,
    UpdateCharacterUseCase,
)
from characters.domain.entities import (
    CharacterNotFoundError,
    CharacterUpdateRequest,
    CloneRequest,
    TemplateNotFoundError,
)
from characters.infrastructure.database import (
    Base,
    CharacterRepository,
    create_engine_from_url,
    create_session_factory,
)
from characters.infrastructure.prototypes import build_default_registry

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://app:secret@db:5432/appdb"
)

engine = create_engine_from_url(DATABASE_URL)
session_factory = create_session_factory(engine)
registry = build_default_registry()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Create tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Character Template System",
    description="Prototype pattern: clone game character templates",
    version="1.0.0",
    lifespan=lifespan,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: provide a database session per request."""
    async with session_factory() as session:
        async with session.begin():
            yield session


# ── Pydantic schemas ────────────────────────────────────────────────────────


class CloneRequestSchema(BaseModel):
    character_name: str
    overrides: dict[str, Any] = {}


class UpdateRequestSchema(BaseModel):
    name: str | None = None
    stats: dict[str, int] | None = None
    skills: list[str] | None = None
    equipment: list[str] | None = None
    level: int | None = None


class CharacterResponse(BaseModel):
    id: int
    name: str
    template_name: str
    stats_json: dict[str, int]


# ── Routes ──────────────────────────────────────────────────────────────────


@app.get("/characters/templates", summary="List available templates")
def list_templates() -> dict[str, list[str]]:
    """Return all registered character templates."""
    use_case = ListTemplatesUseCase(registry)
    return {"templates": use_case.execute()}


@app.post(
    "/characters/clone/{template_name}",
    response_model=CharacterResponse,
    summary="Clone a character template",
)
async def clone_character(
    template_name: str,
    body: CloneRequestSchema,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Clone the named template with optional attribute overrides."""
    repo = CharacterRepository(session)
    use_case = CloneCharacterUseCase(registry, repo)
    request = CloneRequest(
        character_name=template_name,
        overrides=body.overrides,
    )
    try:
        record = await use_case.execute(request)
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "id": record.id,
        "name": record.name,
        "template_name": record.template_name,
        "stats_json": record.stats_json,
    }


@app.get(
    "/characters",
    response_model=list[CharacterResponse],
    summary="List all characters",
)
async def list_characters(
    session: AsyncSession = Depends(get_session),
) -> list[dict[str, Any]]:
    """Return all persisted characters."""
    repo = CharacterRepository(session)
    use_case = ListCharactersUseCase(repo)
    records = await use_case.execute()
    return [
        {
            "id": r.id,
            "name": r.name,
            "template_name": r.template_name,
            "stats_json": r.stats_json,
        }
        for r in records
    ]


@app.put(
    "/characters/{character_id}",
    response_model=CharacterResponse,
    summary="Update a character",
)
async def update_character(
    character_id: int,
    body: UpdateRequestSchema,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Update an existing character's attributes."""
    repo = CharacterRepository(session)
    use_case = UpdateCharacterUseCase(repo)
    request = CharacterUpdateRequest(
        name=body.name,
        stats=body.stats,
        skills=body.skills,
        equipment=body.equipment,
        level=body.level,
    )
    try:
        record = await use_case.execute(character_id, request)
    except CharacterNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "id": record.id,
        "name": record.name,
        "template_name": record.template_name,
        "stats_json": record.stats_json,
    }
