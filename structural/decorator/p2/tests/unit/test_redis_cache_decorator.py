"""Unit tests for RedisCacheDecorator — uses fakeredis, no mocking of Redis."""

from __future__ import annotations

from unittest.mock import MagicMock

import fakeredis

from cache_decorator.domain.entities import DataQuery, DataResult
from cache_decorator.domain.interfaces import DataService
from cache_decorator.infrastructure.redis_cache_decorator import RedisCacheDecorator


def test_cache_miss_calls_wrapped_and_stores_result(
    mock_wrapped: MagicMock,
    fake_redis_client: fakeredis.FakeRedis,
    sample_query: DataQuery,
    sample_result: DataResult,
) -> None:
    mock_wrapped.get_data.return_value = sample_result
    decorator = RedisCacheDecorator(mock_wrapped, fake_redis_client, ttl_seconds=30)

    result = decorator.get_data(sample_query)

    mock_wrapped.get_data.assert_called_once_with(sample_query)
    assert result == sample_result
    assert fake_redis_client.get(sample_query.cache_key()) is not None


def test_cache_hit_does_not_call_wrapped(
    mock_wrapped: MagicMock,
    fake_redis_client: fakeredis.FakeRedis,
    sample_query: DataQuery,
    sample_result: DataResult,
) -> None:
    mock_wrapped.get_data.return_value = sample_result
    decorator = RedisCacheDecorator(mock_wrapped, fake_redis_client, ttl_seconds=30)
    decorator.get_data(sample_query)  # populates the cache (1st call → miss)
    mock_wrapped.get_data.reset_mock()

    result = decorator.get_data(sample_query)  # should be a hit now

    mock_wrapped.get_data.assert_not_called()
    assert result == sample_result


def test_ttl_is_applied(
    mock_wrapped: MagicMock,
    fake_redis_client: fakeredis.FakeRedis,
    sample_query: DataQuery,
    sample_result: DataResult,
) -> None:
    mock_wrapped.get_data.return_value = sample_result
    decorator = RedisCacheDecorator(mock_wrapped, fake_redis_client, ttl_seconds=42)

    decorator.get_data(sample_query)

    ttl = fake_redis_client.ttl(sample_query.cache_key())
    assert ttl == 42


def test_decorator_satisfies_data_service(
    mock_wrapped: MagicMock, fake_redis_client: fakeredis.FakeRedis
) -> None:
    decorator = RedisCacheDecorator(mock_wrapped, fake_redis_client)
    assert isinstance(decorator, DataService)
