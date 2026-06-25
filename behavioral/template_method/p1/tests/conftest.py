"""Shared pytest fixtures for the Data Import Pipeline tests.

PostgreSQL is not assumed to be available when running `pytest` outside of
docker-compose, so `PostgresImportRepository.bulk_insert` is patched at the
`DataImporter.persist` boundary. This keeps tests fast and hermetic while
still exercising the full Template Method algorithm (read_raw -> parse ->
validate -> transform -> persist -> generate_report) end-to-end through the
FastAPI HTTP layer.
"""

from __future__ import annotations

import os
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def database_url_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide a DATABASE_URL so PostgresImportRepository.__init__ does not
    raise KeyError when instantiated, even though no real connection is made
    (bulk_insert itself is mocked by `mocked_bulk_insert`).
    """
    monkeypatch.setenv(
        "DATABASE_URL",
        os.environ.get("DATABASE_URL", "postgresql://app:secret@db:5432/appdb"),
    )


@pytest.fixture
def mocked_bulk_insert() -> Generator[MagicMock, None, None]:
    """Patch PostgresImportRepository.bulk_insert to avoid a real database.

    Returns the count of records passed in, mimicking a successful insert
    of every record.
    """

    def fake_bulk_insert(self: object, records: list[dict[str, object]]) -> int:
        return len(records)

    with patch(
        "data_import.infrastructure.postgres_repository.PostgresImportRepository.bulk_insert",
        autospec=True,
        side_effect=fake_bulk_insert,
    ) as mock:
        yield mock


@pytest.fixture
def client(mocked_bulk_insert: MagicMock) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with the database layer mocked out."""
    from main import app

    with TestClient(app) as test_client:
        yield test_client
