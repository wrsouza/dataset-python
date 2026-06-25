"""Shared pytest fixtures for the Form State Save/Restore tests."""

from __future__ import annotations

import fakeredis
import pytest
from flask.testing import FlaskClient
from redis import Redis

from form_state_memento.app import create_app
from form_state_memento.infrastructure.caretaker import RedisFormCaretaker


@pytest.fixture
def fake_redis() -> Redis:
    return fakeredis.FakeRedis()


@pytest.fixture
def caretaker(fake_redis: Redis) -> RedisFormCaretaker:
    return RedisFormCaretaker(fake_redis)


@pytest.fixture
def client(caretaker: RedisFormCaretaker) -> FlaskClient:
    app = create_app(caretaker=caretaker)
    app.config.update(TESTING=True)
    return app.test_client()
