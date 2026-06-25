"""Application use cases for the Cache Manager project."""

from __future__ import annotations

from typing import Any

from cache.domain.entities import Product
from cache.domain.interfaces import CacheManager, CacheStats


class GetProductsUseCase:
    """Return all products, reading from cache when available.

    Demonstrates the cache-aside pattern: check cache first, fall back
    to the data source, then populate cache for subsequent requests.
    """

    CACHE_KEY = "products:all"
    CACHE_TTL = 60

    def __init__(self, cache: CacheManager) -> None:
        self._cache = cache

    def execute(self) -> list[dict[str, Any]]:
        cached: list[dict[str, Any]] | None = self._cache.get(self.CACHE_KEY)
        if cached is not None:
            return cached

        # Simulate a slow database read.
        products = self._load_from_db()
        self._cache.set(self.CACHE_KEY, products, ttl=self.CACHE_TTL)
        return products

    @staticmethod
    def _load_from_db() -> list[dict[str, Any]]:
        """Fake data source — in production this would be a repository."""
        return [
            Product(1, "Widget Alpha", 9.99, "hardware").to_dict(),
            Product(2, "Widget Beta", 19.99, "hardware").to_dict(),
            Product(3, "Service Pro", 99.00, "software").to_dict(),
        ]


class FlushCacheUseCase:
    """Evict all keys from the cache."""

    def __init__(self, cache: CacheManager) -> None:
        self._cache = cache

    def execute(self) -> bool:
        return self._cache.flush()


class GetCacheStatsUseCase:
    """Return current cache statistics."""

    def __init__(self, cache: CacheManager) -> None:
        self._cache = cache

    def execute(self) -> CacheStats:
        return self._cache.get_stats()
