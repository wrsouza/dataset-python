"""Domain interfaces for the Cache Manager.

Abstractions keep the application layer independent of Redis or
any specific cache backend (DIP + OCP).
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Any, Protocol


class CircuitState(Enum):
    """States of the circuit breaker automaton.

    CLOSED  -> normal operation, requests flow through.
    OPEN    -> backend is down; requests fail fast without hitting Redis.
    HALF_OPEN -> probe state; one request is allowed to test recovery.
    """

    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class CacheBackend(Protocol):
    """Minimal contract for any cache backend (Redis, Memcached, in-memory).

    OCP: adding a new backend (e.g. Memcached) means creating a new class
    that satisfies this Protocol — no changes to CacheManager.
    ISP: only the operations actually needed are declared here.
    """

    def get(self, key: str) -> Any:
        """Return the value for key, or None if absent/expired."""
        ...

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Store value under key with a TTL in seconds. Returns True on success."""
        ...

    def delete(self, key: str) -> bool:
        """Remove a key. Returns True if the key existed."""
        ...

    def flush(self) -> bool:
        """Evict all keys. Returns True on success."""
        ...

    def ping(self) -> bool:
        """Return True if the backend is reachable."""
        ...


class CacheManager(Protocol):
    """High-level cache interface consumed by the application layer.

    Includes circuit breaker semantics so callers never need to handle
    backend failures directly.
    """

    def get(self, key: str) -> Any: ...

    def set(self, key: str, value: Any, ttl: int = 300) -> bool: ...

    def delete(self, key: str) -> bool: ...

    def flush(self) -> bool: ...

    def get_stats(self) -> CacheStats: ...

    @property
    def circuit_state(self) -> CircuitState: ...


class CacheStats(Protocol):
    """Statistics snapshot from the cache manager."""

    @property
    def hits(self) -> int: ...

    @property
    def misses(self) -> int: ...

    @property
    def circuit_state(self) -> CircuitState: ...

    def to_dict(self) -> dict[str, Any]: ...
