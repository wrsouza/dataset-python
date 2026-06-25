"""Shared pytest fixtures for the Shopping Cart Visitors tests."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest
from flask.testing import FlaskClient

from shopping_cart_visitors.app import create_app
from shopping_cart_visitors.infrastructure.repository import CartReportRepository


@pytest.fixture
def connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def repository(connection: sqlite3.Connection) -> CartReportRepository:
    return CartReportRepository(connection, dialect="sqlite")


@pytest.fixture
def client(repository: CartReportRepository) -> FlaskClient:
    app = create_app(repository=repository)
    app.config.update(TESTING=True)
    return app.test_client()
