"""Unit tests for PostgresUserProfileService (RealSubject) — asyncpg pool mocked."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from lazy_loading.domain.exceptions import AvatarNotFoundError, UserNotFoundError
from lazy_loading.infrastructure.real_subject import PostgresUserProfileService


def _make_pool_with_connection(conn: MagicMock) -> MagicMock:
    pool = MagicMock()

    @asynccontextmanager
    async def acquire() -> object:
        yield conn

    pool.acquire = acquire
    return pool


async def test_get_profile_returns_user_profile() -> None:
    conn = MagicMock()
    conn.fetchrow = AsyncMock(
        return_value={
            "user_id": 1,
            "username": "alice",
            "email": "alice@example.com",
            "full_name": "Alice Anderson",
            "created_at": datetime(2024, 1, 1),
            "is_active": True,
        }
    )
    service = PostgresUserProfileService(pool=_make_pool_with_connection(conn))

    profile = await service.get_profile(1)

    assert profile.username == "alice"


async def test_get_profile_raises_when_row_is_none() -> None:
    conn = MagicMock()
    conn.fetchrow = AsyncMock(return_value=None)
    service = PostgresUserProfileService(pool=_make_pool_with_connection(conn))

    with pytest.raises(UserNotFoundError):
        await service.get_profile(999)


async def test_get_avatar_raises_when_row_is_none() -> None:
    conn = MagicMock()
    conn.fetchrow = AsyncMock(return_value=None)
    service = PostgresUserProfileService(pool=_make_pool_with_connection(conn))

    with pytest.raises(AvatarNotFoundError):
        await service.get_avatar(1)


async def test_get_documents_returns_empty_list_when_no_rows() -> None:
    conn = MagicMock()
    conn.fetch = AsyncMock(return_value=[])
    service = PostgresUserProfileService(pool=_make_pool_with_connection(conn))

    documents = await service.get_documents(1)

    assert documents == []


async def test_get_analytics_raises_when_row_is_none() -> None:
    conn = MagicMock()
    conn.fetchrow = AsyncMock(return_value=None)
    service = PostgresUserProfileService(pool=_make_pool_with_connection(conn))

    with pytest.raises(UserNotFoundError):
        await service.get_analytics(1)
