"""Unit tests for the decorator composition factory."""

from __future__ import annotations

import fakeredis

from cache_decorator.domain.interfaces import DataService
from cache_decorator.infrastructure.factory import build_data_service
from cache_decorator.infrastructure.logging_decorator import LoggingDecorator
from cache_decorator.infrastructure.product_quote_service import ProductQuoteService
from cache_decorator.infrastructure.redis_cache_decorator import RedisCacheDecorator
from cache_decorator.infrastructure.retry_decorator import RetryDecorator


def test_build_data_service_stacks_decorators_in_expected_order(
    fake_redis_client: fakeredis.FakeRedis,
) -> None:
    service = build_data_service(
        redis_client=fake_redis_client,
        cache_ttl_seconds=10,
        retry_max_attempts=2,
        retry_backoff_seconds=0.0,
    )

    assert isinstance(service, DataService)
    assert isinstance(service, RetryDecorator)
    assert isinstance(service._wrapped, LoggingDecorator)  # noqa: SLF001
    assert isinstance(service._wrapped._wrapped, RedisCacheDecorator)  # noqa: SLF001
    assert isinstance(
        service._wrapped._wrapped._wrapped, ProductQuoteService  # noqa: SLF001
    )
