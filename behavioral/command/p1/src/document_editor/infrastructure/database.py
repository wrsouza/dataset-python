"""SQLAlchemy engine/session factory wiring for the service."""

from __future__ import annotations

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from document_editor.infrastructure.models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://app:secret@db:5432/appdb"
)

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create all tables if they do not exist yet."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency yielding a database session per request."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
