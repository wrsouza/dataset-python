"""Unit tests for the Singleton pattern in DatabasePool.

Key assertion: multiple calls to DatabasePool() must return the *same* object
(identity check with `is`), regardless of thread or call site.
"""

from __future__ import annotations

import threading
from typing import Any

import pytest

from db_pool.infrastructure.singleton import DatabasePool, SingletonMeta


# ── Reset helper ─────────────────────────────────────────────────────────────
# Each test that modifies the singleton registry must clean up afterwards to
# avoid polluting other tests.

@pytest.fixture(autouse=True)
def reset_singleton() -> Any:
    """Remove DatabasePool from the registry before and after each test."""
    SingletonMeta._instances.pop(DatabasePool, None)
    yield
    SingletonMeta._instances.pop(DatabasePool, None)


# ── Singleton identity tests ──────────────────────────────────────────────────

def test_same_instance_on_repeated_calls() -> None:
    """Two successive calls to DatabasePool() must return the same object."""
    first = DatabasePool()
    second = DatabasePool()
    assert first is second, "Singleton violated: two distinct instances created"


def test_same_instance_identity_id() -> None:
    """id() must be identical for all references."""
    a = DatabasePool()
    b = DatabasePool()
    c = DatabasePool()
    assert id(a) == id(b) == id(c)


def test_singleton_under_thread_contention() -> None:
    """Simulate 50 threads racing to obtain the singleton simultaneously.

    All threads must receive the exact same object — no two distinct instances.
    """
    instances: list[DatabasePool] = []
    lock = threading.Lock()

    def grab() -> None:
        instance = DatabasePool()
        with lock:
            instances.append(instance)

    threads = [threading.Thread(target=grab) for _ in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(instances) == 50
    first = instances[0]
    assert all(inst is first for inst in instances), (
        "Thread-safety violated: multiple distinct DatabasePool instances created"
    )


def test_pool_not_ready_before_initialise() -> None:
    """is_ready must be False before initialise() is called."""
    pool = DatabasePool()
    assert not pool.is_ready


@pytest.mark.asyncio
async def test_acquire_raises_before_initialise() -> None:
    """acquire() on an uninitialised pool raises RuntimeError with a clear message."""
    pool = DatabasePool()
    with pytest.raises(RuntimeError, match="not been initialised"):
        await pool.acquire()


@pytest.mark.asyncio
async def test_get_stats_before_initialise_returns_zeros() -> None:
    """get_stats() before initialise returns a zeroed snapshot — no crash."""
    pool = DatabasePool()
    stats = await pool.get_stats()
    assert stats.size == 0
    assert stats.free == 0
    assert stats.used == 0


# ── Use case tests (with fakes) ───────────────────────────────────────────────

class FakePool:
    """In-memory fake that satisfies the ConnectionPool protocol."""

    async def get_stats(self) -> Any:
        from db_pool.domain.entities import PoolStatsSnapshot
        from datetime import datetime
        return PoolStatsSnapshot(size=5, free=3, used=2, min_size=2, max_size=10, sampled_at=datetime.utcnow())

    async def acquire(self) -> None:
        return None

    async def release(self, connection: Any) -> None:
        pass

    async def close(self) -> None:
        pass


@pytest.mark.asyncio
async def test_get_pool_stats_use_case() -> None:
    from db_pool.application.use_cases import GetPoolStatsUseCase
    pool = FakePool()
    stats = await GetPoolStatsUseCase(pool).execute()  # type: ignore[arg-type]
    assert stats.size == 5
    assert stats.used == 2
    assert stats.free == 3


@pytest.mark.asyncio
async def test_create_user_use_case_validates_email() -> None:
    """CreateUserUseCase rejects emails without '@'."""
    from db_pool.application.use_cases import CreateUserUseCase
    from db_pool.domain.entities import CreateUserRequest

    class FakeRepo:
        async def create(self, name: str, email: str) -> dict:
            return {"id": 1, "name": name, "email": email, "created_at": "2024-01-01"}

        async def find_all(self) -> list:
            return []

        async def find_by_id(self, user_id: int) -> None:
            return None

    use_case = CreateUserUseCase(FakeRepo())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="valid email"):
        await use_case.execute(CreateUserRequest(name="Alice", email="notanemail"))


@pytest.mark.asyncio
async def test_create_user_use_case_validates_blank_name() -> None:
    from db_pool.application.use_cases import CreateUserUseCase
    from db_pool.domain.entities import CreateUserRequest

    class FakeRepo:
        async def create(self, name: str, email: str) -> dict:
            return {}

        async def find_all(self) -> list:
            return []

        async def find_by_id(self, user_id: int) -> None:
            return None

    use_case = CreateUserUseCase(FakeRepo())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="blank"):
        await use_case.execute(CreateUserRequest(name="   ", email="a@b.com"))


def test_pool_stats_snapshot_to_dict() -> None:
    from datetime import datetime
    from db_pool.domain.entities import PoolStatsSnapshot
    snap = PoolStatsSnapshot(size=10, free=7, used=3, min_size=2, max_size=10, sampled_at=datetime(2024, 1, 1))
    d = snap.to_dict()
    assert d["size"] == 10
    assert d["free"] == 7
    assert d["used"] == 3
