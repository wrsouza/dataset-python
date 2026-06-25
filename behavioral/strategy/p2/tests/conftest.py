"""Shared pytest fixtures for the Discount Strategy API tests."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest
from flask.testing import FlaskClient

from discount_strategy_api.app import create_app
from discount_strategy_api.infrastructure.repository import DiscountHistoryRepository


@pytest.fixture
def connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def repository(connection: sqlite3.Connection) -> DiscountHistoryRepository:
    return DiscountHistoryRepository(connection, dialect="sqlite")


@pytest.fixture
def client(repository: DiscountHistoryRepository) -> FlaskClient:
    app = create_app(repository=repository)
    app.config.update(TESTING=True)
    return app.test_client()
