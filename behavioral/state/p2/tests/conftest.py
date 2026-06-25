"""Shared pytest fixtures for the User Auth Session FSM tests."""

from __future__ import annotations

import fakeredis
import pytest
from flask.testing import FlaskClient
from redis import Redis

from auth_session_fsm.app import create_app
from auth_session_fsm.infrastructure.repository import RedisSessionRepository


@pytest.fixture
def fake_redis() -> Redis:
    return fakeredis.FakeRedis()


@pytest.fixture
def repository(fake_redis: Redis) -> RedisSessionRepository:
    return RedisSessionRepository(fake_redis)


@pytest.fixture
def client(repository: RedisSessionRepository) -> FlaskClient:
    app = create_app(repository=repository)
    app.config.update(TESTING=True)
    return app.test_client()
