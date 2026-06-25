"""Proxy: RedisCacheProxy — Cache Proxy implementation.

Intercepts calls to ExternalAPIService, checks Redis before calling the
real subject, caches the result on miss, and exposes cache statistics.

Pattern roles:
  - Subject:     ExternalAPIService (Protocol in domain/interfaces.py)
  - RealSubject: MockExternalAPIService (infrastructure/real_subject.py)
  - Proxy:       RedisCacheProxy (this file)

TTLs:
  - weather:       300 s  (data changes every few minutes)
  - exchange_rate: 3600 s (hourly refresh is sufficient for most use cases)
  - stock_price:   60 s   (volatile, needs fresher data)
"""

from __future__ import annotations

import json
import logging

import redis

from cache_proxy.domain.entities import CacheStats, StockData, WeatherData
from cache_proxy.domain.exceptions import CacheBackendError
from cache_proxy.domain.interfaces import ExternalAPIService

logger = logging.getLogger(__name__)

_TTL_WEATHER: int = 300
_TTL_EXCHANGE: int = 3600
_TTL_STOCK: int = 60


def _weather_key(city: str) -> str:
    return f"weather:{city.lower()}"


def _exchange_key(from_cur: str, to_cur: str) -> str:
    return f"exchange:{from_cur.upper()}:{to_cur.upper()}"


def _stock_key(ticker: str) -> str:
    return f"stock:{ticker.upper()}"


class RedisCacheProxy:
    """Cache Proxy that wraps ExternalAPIService with a Redis backing store.

    Clients code against ExternalAPIService, so they are fully unaware
    whether they hold a RedisCacheProxy or the real service — LSP is
    preserved. The proxy is responsible solely for caching decisions
    (SRP), and it depends on the ExternalAPIService abstraction (DIP).
    """

    def __init__(self, wrapped: ExternalAPIService, redis_client: redis.Redis) -> None:
        self._wrapped = wrapped
        self._redis = redis_client
        self._stats = CacheStats()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _get_cached(self, key: str) -> dict | None:  # type: ignore[type-arg]
        try:
            raw = self._redis.get(key)
        except redis.RedisError as exc:
            raise CacheBackendError(str(exc)) from exc
        if raw is None:
            return None
        return json.loads(raw)  # type: ignore[no-any-return]

    def _set_cached(self, key: str, data: dict, ttl: int) -> None:  # type: ignore[type-arg]
        try:
            self._redis.setex(key, ttl, json.dumps(data))
        except redis.RedisError as exc:
            # Cache write failure is non-fatal: log and continue
            logger.warning("Cache write failed for key %r: %s", key, exc)

    def _record_hit(self) -> None:
        self._stats.hits += 1

    def _record_miss(self) -> None:
        self._stats.misses += 1

    # ── ExternalAPIService interface ─────────────────────────────────────────

    def get_weather(self, city: str) -> WeatherData:
        """Return weather data from cache or delegate to real subject."""
        key = _weather_key(city)
        cached = self._get_cached(key)
        if cached is not None:
            self._record_hit()
            logger.debug("Cache HIT for %s", key)
            return WeatherData(**cached)

        self._record_miss()
        logger.debug("Cache MISS for %s — calling real subject", key)
        result = self._wrapped.get_weather(city)
        self._set_cached(key, result.__dict__, _TTL_WEATHER)
        return result

    def get_exchange_rate(self, from_cur: str, to_cur: str) -> float:
        """Return exchange rate from cache or delegate to real subject."""
        key = _exchange_key(from_cur, to_cur)
        cached = self._get_cached(key)
        if cached is not None:
            self._record_hit()
            logger.debug("Cache HIT for %s", key)
            return float(cached["rate"])

        self._record_miss()
        logger.debug("Cache MISS for %s — calling real subject", key)
        rate = self._wrapped.get_exchange_rate(from_cur, to_cur)
        self._set_cached(key, {"rate": rate}, _TTL_EXCHANGE)
        return rate

    def get_stock_price(self, ticker: str) -> StockData:
        """Return stock data from cache or delegate to real subject."""
        key = _stock_key(ticker)
        cached = self._get_cached(key)
        if cached is not None:
            self._record_hit()
            logger.debug("Cache HIT for %s", key)
            return StockData(**cached)

        self._record_miss()
        logger.debug("Cache MISS for %s — calling real subject", key)
        result = self._wrapped.get_stock_price(ticker)
        self._set_cached(key, result.__dict__, _TTL_STOCK)
        return result

    # ── proxy-specific ────────────────────────────────────────────────────────

    def get_stats(self) -> CacheStats:
        """Return accumulated cache statistics."""
        return self._stats

    def flush(self) -> int:
        """Flush all proxy-managed keys from Redis.

        Returns the number of keys removed.
        """
        try:
            keys = (
                self._redis.keys("weather:*")
                + self._redis.keys("exchange:*")
                + self._redis.keys("stock:*")
            )
            if not keys:
                return 0
            return self._redis.delete(*keys)
        except redis.RedisError as exc:
            raise CacheBackendError(str(exc)) from exc
