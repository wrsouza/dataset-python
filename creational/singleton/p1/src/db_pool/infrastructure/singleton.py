"""Singleton DatabasePool implementation using a thread-safe metaclass.

Pattern: Singleton via Metaclass + threading.Lock
Thread-safety: double-checked locking guarantees exactly one instance even
when multiple coroutines or threads race during startup.
"""

from __future__ import annotations

import asyncio
import threading
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncIterator, ClassVar

import asyncpg  # type: ignore[import]

from db_pool.domain.entities import PoolStatsSnapshot


class SingletonMeta(type):
    """Metaclass that enforces Singleton semantics with thread-safety.

    Using a metaclass (rather than __new__) keeps the business class clean:
    DatabasePool only expresses pool logic, not lifecycle management.

    _instances maps each class to its sole instance.
    _lock serialises creation races across OS-level threads.
    """

    _instances: ClassVar[dict[type, Any]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        # Fast path: instance already created — no locking needed.
        if cls not in cls._instances:
            with cls._lock:
                # Slow path: re-check inside the lock to handle the case
                # where two threads both saw the instance as absent.
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class DatabasePool(metaclass=SingletonMeta):
    """Async PostgreSQL connection pool shared across all FastAPI requests.

    SRP: this class is solely responsible for managing the asyncpg pool.
    It does not know about HTTP, business logic, or user entities.

    Lifecycle:
      1. FastAPI lifespan calls `await DatabasePool().initialise(dsn, ...)`
      2. All endpoints receive the same instance via dependency injection.
      3. FastAPI lifespan calls `await DatabasePool().close()` on shutdown.
    """

    def __init__(self) -> None:
        # Guard: __init__ runs once because SingletonMeta ensures a single
        # instance, but we still protect against accidental re-initialisation.
        self._pool: asyncpg.Pool | None = None
        self._min_size: int = 2
        self._max_size: int = 10
        self._initialised: bool = False
        # asyncio.Lock for coroutine-level safety inside the event loop.
        self._async_lock: asyncio.Lock = asyncio.Lock()

    async def initialise(
        self,
        dsn: str,
        min_size: int = 2,
        max_size: int = 10,
    ) -> None:
        """Create the underlying asyncpg pool exactly once."""
        if self._initialised:
            return
        async with self._async_lock:
            if self._initialised:
                return
            self._pool = await asyncpg.create_pool(
                dsn,
                min_size=min_size,
                max_size=max_size,
            )
            self._min_size = min_size
            self._max_size = max_size
            self._initialised = True

    async def acquire(self) -> asyncpg.Connection:
        """Borrow a connection from the pool.

        Raises RuntimeError if the pool has not been initialised,
        giving a clear error instead of an AttributeError deep in asyncpg.
        """
        if self._pool is None:
            raise RuntimeError("DatabasePool has not been initialised. Call initialise() first.")
        return await self._pool.acquire()

    async def release(self, connection: asyncpg.Connection) -> None:
        """Return a connection to the pool."""
        if self._pool is None:
            return
        await self._pool.release(connection)

    @asynccontextmanager
    async def connection(self) -> AsyncIterator[asyncpg.Connection]:
        """Async context manager for safe connection borrowing.

        Guarantees release even if the caller raises an exception.

        Usage:
            async with pool.connection() as conn:
                row = await conn.fetchrow("SELECT 1")
        """
        conn = await self.acquire()
        try:
            yield conn
        finally:
            await self.release(conn)

    async def get_stats(self) -> PoolStatsSnapshot:
        """Sample the current pool state as an immutable snapshot."""
        if self._pool is None:
            return PoolStatsSnapshot(
                size=0,
                free=0,
                used=0,
                min_size=self._min_size,
                max_size=self._max_size,
                sampled_at=datetime.utcnow(),
            )
        size = self._pool.get_size()
        idle = self._pool.get_idle_size()
        return PoolStatsSnapshot(
            size=size,
            free=idle,
            used=size - idle,
            min_size=self._min_size,
            max_size=self._max_size,
            sampled_at=datetime.utcnow(),
        )

    async def close(self) -> None:
        """Drain and close all connections gracefully."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            self._initialised = False

    @property
    def is_ready(self) -> bool:
        """True when the pool is open and ready for requests."""
        return self._initialised and self._pool is not None
