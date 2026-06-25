"""Domain exceptions for the cache_proxy package."""

from __future__ import annotations


class CacheBackendError(Exception):
    """Raised when the Redis cache backend is unavailable."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Cache backend error: {reason}")
