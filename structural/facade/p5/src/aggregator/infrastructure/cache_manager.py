"""In-memory TTL cache — the Facade's subsystem for avoiding redundant API calls."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

from aggregator.domain.interfaces import CacheManager

T = TypeVar("T")


class InMemoryCacheManager(CacheManager):
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, object]] = {}

    def get_or_fetch(self, key: str, ttl_seconds: int, fetcher: Callable[[], T]) -> T:
        now = time.monotonic()
        cached = self._store.get(key)
        if cached is not None:
            expires_at, value = cached
            if now < expires_at:
                return value  # type: ignore[return-value]

        value = fetcher()
        self._store[key] = (now + ttl_seconds, value)
        return value

    def clear(self) -> None:
        self._store.clear()

    def size(self) -> int:
        return len(self._store)
