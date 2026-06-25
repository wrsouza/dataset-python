"""Composition helper: builds the decorated DataService chain.

Pattern role: this is where decorators are stacked around the
ConcreteComponent. Adding a new decorator (e.g. metrics) means writing
a new class and adding one line here — no existing decorator or the
ConcreteComponent needs to change (OCP).
"""

from __future__ import annotations

import redis

from cache_decorator.domain.interfaces import DataService
from cache_decorator.infrastructure.logging_decorator import LoggingDecorator
from cache_decorator.infrastructure.product_quote_service import ProductQuoteService
from cache_decorator.infrastructure.redis_cache_decorator import RedisCacheDecorator
from cache_decorator.infrastructure.retry_decorator import RetryDecorator


def build_data_service(
    redis_client: redis.Redis,
    cache_ttl_seconds: int,
    retry_max_attempts: int,
    retry_backoff_seconds: float,
) -> DataService:
    """Compose ProductQuoteService wrapped by Cache, Logging, and Retry.

    Order (outermost first): Retry -> Logging -> RedisCache -> ProductQuoteService.
    Retry sits outermost so it re-attempts the whole logged/cached call;
    Logging sits around the cache so both hits and misses are observable.
    """
    service: DataService = ProductQuoteService()
    service = RedisCacheDecorator(service, redis_client, ttl_seconds=cache_ttl_seconds)
    service = LoggingDecorator(service)
    service = RetryDecorator(
        service,
        max_attempts=retry_max_attempts,
        backoff_seconds=retry_backoff_seconds,
    )
    return service
