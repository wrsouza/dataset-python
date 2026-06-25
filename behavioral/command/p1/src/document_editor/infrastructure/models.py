"""SQLAlchemy ORM models backing the PostgreSQL persistence adapters."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models in this service."""


class DocumentModel(Base):
    """Row representation of a `Document` aggregate."""

    __tablename__ = "documents"

    document_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    content: Mapped[str] = mapped_column(Text, default="")
    format_ranges: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)


class CommandHistoryModel(Base):
    """Row representation of one entry in a document's command history."""

    __tablename__ = "command_history"

    command_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(64), index=True)
    description: Mapped[str] = mapped_column(Text)
    is_reversible: Mapped[bool] = mapped_column(Boolean, default=True)
    action: Mapped[str] = mapped_column(String(16))
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
