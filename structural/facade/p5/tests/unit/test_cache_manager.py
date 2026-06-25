"""Unit tests for InMemoryCacheManager — TTL expiry and fetcher invocation."""

from __future__ import annotations

import time

from aggregator.infrastructure.cache_manager import InMemoryCacheManager


def test_get_or_fetch_calls_fetcher_on_miss() -> None:
    cache = InMemoryCacheManager()
    calls = []

    result = cache.get_or_fetch(
        "key", ttl_seconds=60, fetcher=lambda: calls.append(1) or "value"
    )

    assert result == "value"
    assert len(calls) == 1


def test_get_or_fetch_returns_cached_value_within_ttl() -> None:
    cache = InMemoryCacheManager()
    call_count = 0

    def fetcher() -> str:
        nonlocal call_count
        call_count += 1
        return f"value-{call_count}"

    first = cache.get_or_fetch("key", ttl_seconds=60, fetcher=fetcher)
    second = cache.get_or_fetch("key", ttl_seconds=60, fetcher=fetcher)

    assert first == second == "value-1"
    assert call_count == 1


def test_get_or_fetch_refetches_after_ttl_expires() -> None:
    cache = InMemoryCacheManager()
    call_count = 0

    def fetcher() -> str:
        nonlocal call_count
        call_count += 1
        return f"value-{call_count}"

    cache.get_or_fetch("key", ttl_seconds=0, fetcher=fetcher)
    time.sleep(0.01)
    second = cache.get_or_fetch("key", ttl_seconds=0, fetcher=fetcher)

    assert second == "value-2"
    assert call_count == 2


def test_clear_empties_the_cache() -> None:
    cache = InMemoryCacheManager()
    cache.get_or_fetch("key", ttl_seconds=60, fetcher=lambda: "value")

    cache.clear()

    assert cache.size() == 0


def test_size_reflects_distinct_keys() -> None:
    cache = InMemoryCacheManager()
    cache.get_or_fetch("a", ttl_seconds=60, fetcher=lambda: 1)
    cache.get_or_fetch("b", ttl_seconds=60, fetcher=lambda: 2)

    assert cache.size() == 2
