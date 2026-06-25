"""Unit tests for CacheManager Singleton and circuit breaker logic."""

from __future__ import annotations

import threading
from typing import Any
from unittest.mock import MagicMock

import pytest

from cache.domain.interfaces import CircuitState
from cache.infrastructure.singleton import CacheManager, InMemoryBackend


@pytest.fixture(autouse=True)
def reset_singleton() -> Any:
    """Reset the Singleton between tests."""
    CacheManager._instance = None
    yield
    CacheManager._instance = None


# ── Singleton identity ─────────────────────────────────────────────────────


def test_same_instance_on_multiple_calls() -> None:
    a = CacheManager()
    b = CacheManager()
    assert a is b


def test_singleton_identity_across_50_threads() -> None:
    instances: list[CacheManager] = []
    lock = threading.Lock()

    def grab() -> None:
        inst = CacheManager()
        with lock:
            instances.append(inst)

    threads = [threading.Thread(target=grab) for _ in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    first = instances[0]
    assert all(i is first for i in instances)


# ── InMemoryBackend ────────────────────────────────────────────────────────


def test_in_memory_set_and_get() -> None:
    backend = InMemoryBackend()
    backend.set("k", "v", ttl=60)
    assert backend.get("k") == "v"


def test_in_memory_delete() -> None:
    backend = InMemoryBackend()
    backend.set("k", "value", ttl=60)
    backend.delete("k")
    assert backend.get("k") is None


def test_in_memory_flush() -> None:
    backend = InMemoryBackend()
    backend.set("a", 1, ttl=60)
    backend.set("b", 2, ttl=60)
    backend.flush()
    assert backend.get("a") is None
    assert backend.get("b") is None


def test_in_memory_ttl_expiry() -> None:
    import time

    backend = InMemoryBackend()
    backend.set("k", "v", ttl=1)
    time.sleep(1.1)
    assert backend.get("k") is None


def test_in_memory_ping_always_true() -> None:
    assert InMemoryBackend().ping() is True


# ── Circuit Breaker ────────────────────────────────────────────────────────


def test_initial_circuit_state_is_closed() -> None:
    mgr = CacheManager()
    assert mgr.circuit_state == CircuitState.CLOSED


def test_circuit_opens_after_threshold_failures() -> None:
    mgr = CacheManager()
    # Force Redis to be set but always fail.
    failing_backend = MagicMock()
    failing_backend.get.side_effect = ConnectionError("redis down")
    failing_backend.set.side_effect = ConnectionError("redis down")
    mgr._redis = failing_backend

    for _ in range(CacheManager._FAILURE_THRESHOLD):
        mgr.get("any_key")

    assert mgr.circuit_state == CircuitState.OPEN


def test_get_falls_back_to_memory_when_circuit_open() -> None:
    mgr = CacheManager()
    mgr._memory.set("fallback_key", "fallback_value", ttl=60)
    mgr._circuit_state = CircuitState.OPEN
    mgr._opened_at = None  # prevent half-open transition

    # Override _opened_at to prevent half-open transition
    import time

    mgr._opened_at = time.monotonic() + 9999

    result = mgr.get("fallback_key")
    assert result == "fallback_value"


# ── Stats ──────────────────────────────────────────────────────────────────


def test_stats_track_hits_and_misses() -> None:
    mgr = CacheManager()
    mgr._memory.set("x", 42, ttl=60)

    mgr.get("x")  # hit
    mgr.get("y")  # miss

    stats = mgr.get_stats()
    assert stats.hits == 1
    assert stats.misses == 1
    assert stats.hit_rate == 0.5


def test_stats_to_dict_has_required_keys() -> None:
    mgr = CacheManager()
    d = mgr.get_stats().to_dict()
    for key in ("hits", "misses", "hit_rate", "circuit_state", "backend", "sampled_at"):
        assert key in d


# ── Use cases ──────────────────────────────────────────────────────────────


def test_get_products_populates_cache() -> None:
    from cache.application.use_cases import GetProductsUseCase

    mgr = CacheManager()
    uc = GetProductsUseCase(mgr)  # type: ignore[arg-type]

    first = uc.execute()
    cached = mgr.get(GetProductsUseCase.CACHE_KEY)
    assert cached is not None
    assert len(first) == 3


def test_flush_cache_use_case() -> None:
    from cache.application.use_cases import FlushCacheUseCase

    mgr = CacheManager()
    mgr.set("x", 1)
    FlushCacheUseCase(mgr).execute()  # type: ignore[arg-type]
    assert mgr.get("x") is None
