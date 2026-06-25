"""ConcreteDecorator: RedisCacheDecorator — caches results in Redis.

Pattern role: wraps any DataService and short-circuits the call when a
fresh result is already cached, using the query's cache key with a
configurable TTL. SRP: this class only knows about caching, not about
how the data is fetched or logged.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict

import redis

from cache_decorator.domain.entities import DataQuery, DataResult
from cache_decorator.domain.interfaces import DataService, DataServiceDecorator

logger = logging.getLogger(__name__)

DEFAULT_TTL_SECONDS = 60


class RedisCacheDecorator(DataServiceDecorator):
    """Caches `DataResult`s in Redis, keyed by `DataQuery.cache_key()`."""

    def __init__(
        self,
        wrapped: DataService,
        redis_client: redis.Redis,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> None:
        super().__init__(wrapped)
        self._redis = redis_client
        self._ttl_seconds = ttl_seconds

    def get_data(self, query: DataQuery) -> DataResult:
        """Return the cached result if present, otherwise fetch and cache it."""
        key = query.cache_key()
        cached = self._redis.get(key)
        if cached is not None:
            logger.debug("Cache HIT for %s", key)
            return DataResult(**json.loads(cached))

        logger.debug("Cache MISS for %s", key)
        result = self._wrapped.get_data(query)
        self._redis.set(key, json.dumps(asdict(result)), ex=self._ttl_seconds)
        return result
