"""Database connection factory and session management."""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from organization.infrastructure.models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://app:secret@db:5432/orgdb"
)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def create_tables() -> None:
    """Create all tables if they don't exist (idempotent)."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:  # pragma: no cover
    """FastAPI dependency that provides a DB session per request."""
    with SessionLocal() as session:
        yield session  # type: ignore[misc]
