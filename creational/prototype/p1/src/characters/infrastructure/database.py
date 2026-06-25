"""Database infrastructure for character persistence using SQLAlchemy 2.0."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Sequence

from sqlalchemy import JSON, DateTime, Integer, String, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from characters.domain.entities import CharacterRecord


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


class CharacterModel(Base):
    """ORM model for the characters table."""

    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    template_name: Mapped[str] = mapped_column(String(100), nullable=False)
    stats_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    def to_record(self) -> CharacterRecord:
        """Convert ORM model to domain entity."""
        return CharacterRecord(
            id=self.id,
            name=self.name,
            template_name=self.template_name,
            stats_json=self.stats_json,
            created_at=self.created_at,
        )


class CharacterRepository:
    """Repository for character persistence.

    SRP: only responsible for database CRUD, no business logic.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, record: CharacterRecord) -> CharacterRecord:
        """Persist a new character record and return with generated id."""
        model = CharacterModel(
            name=record.name,
            template_name=record.template_name,
            stats_json=record.stats_json,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model.to_record()

    async def find_all(self) -> list[CharacterRecord]:
        """Return all persisted characters."""
        from sqlalchemy import select

        result = await self._session.execute(select(CharacterModel))
        models: Sequence[CharacterModel] = result.scalars().all()
        return [m.to_record() for m in models]

    async def find_by_id(self, character_id: int) -> CharacterRecord | None:
        """Find a character by its primary key."""
        from sqlalchemy import select

        result = await self._session.execute(
            select(CharacterModel).where(CharacterModel.id == character_id)
        )
        model = result.scalar_one_or_none()
        return model.to_record() if model else None

    async def update(
        self, character_id: int, updates: dict[str, Any]
    ) -> CharacterRecord | None:
        """Update a character record by id."""
        from sqlalchemy import select

        result = await self._session.execute(
            select(CharacterModel).where(CharacterModel.id == character_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None

        if "name" in updates:
            model.name = updates["name"]
        if "stats_json" in updates:
            model.stats_json = updates["stats_json"]

        await self._session.flush()
        await self._session.refresh(model)
        return model.to_record()


def create_engine_from_url(database_url: str) -> Any:
    """Create async SQLAlchemy engine from the given URL."""
    return create_async_engine(database_url, echo=False)


def create_session_factory(engine: Any) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory bound to the given engine."""
    return async_sessionmaker(engine, expire_on_commit=False)
