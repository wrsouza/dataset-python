"""Shared pytest fixtures for the Document Editor test suite."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from document_editor.domain.entities import Document
from document_editor.infrastructure.models import Base


@pytest.fixture
def document() -> Document:
    """A fresh, empty document for unit tests."""
    return Document(document_id="doc-1")


@pytest.fixture
def sqlite_session() -> Iterator[Session]:
    """SQLite in-memory session standing in for PostgreSQL in tests.

    Decision: real PostgreSQL is not guaranteed to be reachable when tests
    run outside docker-compose, so persistence integration tests exercise
    the same SQLAlchemy models against SQLite (StaticPool keeps the
    in-memory database alive for the session's lifetime). The Postgres
    repository classes only use portable SQLAlchemy Core/ORM features, so
    behavior is equivalent for the purposes of this test suite.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client() -> Iterator[TestClient]:
    """TestClient wired against the real FastAPI app.

    Decision: the `/documents` endpoints depend on `get_session`, which by
    default opens a PostgreSQL connection. Real PostgreSQL is not
    guaranteed to be reachable when tests run outside docker-compose, so
    this fixture overrides the `get_session` dependency with a SQLite
    in-memory session. `PostgresDocumentRepository` only uses portable
    SQLAlchemy ORM features, so behavior is equivalent for test purposes.
    """
    from document_editor.infrastructure.database import get_session
    from document_editor.main import _invokers, app

    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    test_session_factory = sessionmaker(bind=test_engine)

    def _override_get_session() -> Iterator[Session]:
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = _override_get_session
    _invokers.clear()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
