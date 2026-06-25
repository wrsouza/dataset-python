"""Singleton CacheManager with Circuit Breaker and in-memory fallback.

Pattern: Singleton via __new__ + threading.Lock
Circuit Breaker: CLOSED -> OPEN -> HALF_OPEN -> CLOSED

The CacheManager is the single global instance shared by all Flask
request handlers. It wraps a Redis backend and automatically falls
back to an in-memory dict when Redis is unavailable.
"""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime
from typing import Any, ClassVar

from cache.domain.entities import CacheStatsSnapshot
from cache.domain.interfaces import CircuitState

# ── In-memory fallback backend ─────────────────────────────────────────────


class InMemoryBackend:
    """Thread-safe in-memory cache used when Redis is unreachable.

    OCP: implements the same interface as the Redis backend so CacheManager
    can swap backends transparently.
    """

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float | None]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if expires_at is not None and time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        with self._lock:
            expires_at = time.monotonic() + ttl if ttl > 0 else None
            self._store[key] = (value, expires_at)
            return True

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._store.pop(key, None) is not None

    def flush(self) -> bool:
        with self._lock:
            self._store.clear()
            return True

    def ping(self) -> bool:
        return True


# ── Redis backend ──────────────────────────────────────────────────────────


class RedisBackend:
    """Thin wrapper around redis-py that satisfies the CacheBackend protocol."""

    def __init__(
        self, host: str = "redis", port: int = 6379, password: str = ""
    ) -> None:
        import redis

        self._client = redis.Redis(
            host=host,
            port=port,
            password=password or None,
            decode_responses=False,
            socket_connect_timeout=2,
            socket_timeout=2,
        )

    def get(self, key: str) -> Any:
        raw = self._client.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        serialised = json.dumps(value)
        return bool(self._client.setex(key, ttl, serialised))

    def delete(self, key: str) -> bool:
        return bool(self._client.delete(key))

    def flush(self) -> bool:
        return bool(self._client.flushdb())

    def ping(self) -> bool:
        try:
            return bool(self._client.ping())
        except Exception:
            return False


# ── Singleton CacheManager ─────────────────────────────────────────────────


class CacheManager:
    """Singleton cache manager with circuit breaker and in-memory fallback.

    Singleton via __new__: simpler than a metaclass when the class is the
    primary entry point and we do not need polymorphic Singleton hierarchies.

    Circuit breaker states:
      CLOSED    -> Redis is healthy; all operations go to Redis.
      OPEN      -> Redis is down; requests served from in-memory fallback.
                   After `_recovery_timeout` seconds, transitions to HALF_OPEN.
      HALF_OPEN -> One probe request is sent to Redis. If it succeeds, the
                   circuit closes. If it fails, the circuit reopens.
    """

    _instance: ClassVar[CacheManager | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    # Circuit breaker tunables
    _FAILURE_THRESHOLD: int = 3
    _RECOVERY_TIMEOUT: float = 30.0

    _initialised: bool

    def __new__(cls) -> CacheManager:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialised = False
                    cls._instance = instance
        return cls._instance

    def __init__(self) -> None:
        # Guard: __init__ is called on every CacheManager() call but we only
        # want to configure the backends once.
        if self._initialised:
            return
        self._redis: RedisBackend | None = None
        self._memory: InMemoryBackend = InMemoryBackend()
        self._circuit_state: CircuitState = CircuitState.CLOSED
        self._failure_count: int = 0
        self._opened_at: float | None = None
        self._hits: int = 0
        self._misses: int = 0
        self._op_lock = threading.Lock()
        self._initialised = True

    def configure(
        self, host: str = "redis", port: int = 6379, password: str = ""
    ) -> None:
        """Connect to Redis. Call once at application startup."""
        self._redis = RedisBackend(host=host, port=port, password=password)
        if self._redis.ping():
            self._circuit_state = CircuitState.CLOSED
        else:
            # Redis unreachable at startup — open the circuit immediately.
            self._trip_breaker()

    # ── Circuit breaker helpers ──────────────────────────────────────────────

    def _trip_breaker(self) -> None:
        self._circuit_state = CircuitState.OPEN
        self._opened_at = time.monotonic()

    def _try_half_open(self) -> bool:
        """Transition from OPEN to HALF_OPEN if the recovery timeout elapsed."""
        if self._circuit_state != CircuitState.OPEN:
            return False
        if self._opened_at is None:
            return False
        elapsed = time.monotonic() - self._opened_at
        if elapsed >= self._RECOVERY_TIMEOUT:
            self._circuit_state = CircuitState.HALF_OPEN
            return True
        return False

    def _active_backend(self) -> Any:
        """Choose the backend based on circuit state."""
        if self._circuit_state == CircuitState.CLOSED:
            return self._redis or self._memory
        if self._circuit_state == CircuitState.OPEN:
            self._try_half_open()
            return self._memory
        # HALF_OPEN: attempt Redis probe
        return self._redis or self._memory

    def _record_success(self) -> None:
        if self._circuit_state == CircuitState.HALF_OPEN:
            self._circuit_state = CircuitState.CLOSED
            self._failure_count = 0

    def _record_failure(self) -> None:
        self._failure_count += 1
        if self._failure_count >= self._FAILURE_THRESHOLD:
            self._trip_breaker()
        elif self._circuit_state == CircuitState.HALF_OPEN:
            # Failed on probe — reopen immediately.
            self._trip_breaker()

    # ── Public API ──────────────────────────────────────────────────────────

    def get(self, key: str) -> Any:
        backend = self._active_backend()
        try:
            value = backend.get(key)
            self._record_success()
            with self._op_lock:
                if value is None:
                    self._misses += 1
                else:
                    self._hits += 1
            return value
        except Exception:
            self._record_failure()
            value = self._memory.get(key)
            with self._op_lock:
                if value is None:
                    self._misses += 1
                else:
                    self._hits += 1
            return value

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        backend = self._active_backend()
        try:
            ok = bool(backend.set(key, value, ttl))
            self._record_success()
            # Mirror to memory for fallback continuity.
            self._memory.set(key, value, ttl)
            return ok
        except Exception:
            self._record_failure()
            return self._memory.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        backend = self._active_backend()
        try:
            ok = bool(backend.delete(key))
            self._record_success()
            self._memory.delete(key)
            return ok
        except Exception:
            self._record_failure()
            return self._memory.delete(key)

    def flush(self) -> bool:
        backend = self._active_backend()
        try:
            ok = bool(backend.flush())
            self._record_success()
            self._memory.flush()
            return ok
        except Exception:
            self._record_failure()
            return self._memory.flush()

    def get_stats(self) -> CacheStatsSnapshot:
        backend_name = (
            "redis"
            if (self._redis is not None and self._circuit_state == CircuitState.CLOSED)
            else "memory"
        )
        return CacheStatsSnapshot(
            hits=self._hits,
            misses=self._misses,
            circuit_state=self._circuit_state,
            backend=backend_name,
            sampled_at=datetime.utcnow(),
        )

    @property
    def circuit_state(self) -> CircuitState:
        return self._circuit_state
