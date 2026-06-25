"""Shared pytest fixtures for Session Token Cache tests."""

from __future__ import annotations

from collections.abc import Iterator

import fakeredis
import pytest
import redis

from session_cache.infrastructure.factory import RedisSessionMetadataFactory
from session_cache.infrastructure.repository import RedisSessionRepository


@pytest.fixture
def fake_redis() -> Iterator[redis.Redis]:
    server = fakeredis.FakeServer()
    client = fakeredis.FakeStrictRedis(server=server)
    yield client
    client.flushall()


@pytest.fixture
def factory(fake_redis: redis.Redis) -> RedisSessionMetadataFactory:
    return RedisSessionMetadataFactory(
        redis_client=fake_redis, app_version="1.0.0-test"
    )


@pytest.fixture
def repository(
    fake_redis: redis.Redis, factory: RedisSessionMetadataFactory
) -> RedisSessionRepository:
    return RedisSessionRepository(redis_client=fake_redis, factory=factory)
