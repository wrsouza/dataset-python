"""Shared fixtures — a Fake RealSubject standing in for PostgresUserProfileService."""

from __future__ import annotations

from datetime import datetime

import pytest

from lazy_loading.domain.entities import (
    UserAnalytics,
    UserAvatar,
    UserDocument,
    UserProfile,
)
from lazy_loading.domain.exceptions import AvatarNotFoundError, UserNotFoundError
from lazy_loading.infrastructure.proxy import LazyUserProfileProxy


class FakeUserProfileService:
    """Implements the same Subject Protocol as PostgresUserProfileService,
    backed by in-memory dicts instead of asyncpg — no real DB required.

    Tracks call_count per method so tests can assert the Proxy actually
    skips redundant calls to this RealSubject (the whole point of Proxy).
    """

    def __init__(self) -> None:
        self.call_counts: dict[str, int] = {
            "get_profile": 0,
            "get_avatar": 0,
            "get_documents": 0,
            "get_analytics": 0,
        }
        self._profiles = {
            1: UserProfile(
                user_id=1,
                username="alice",
                email="alice@example.com",
                full_name="Alice Anderson",
                created_at=datetime(2024, 1, 1),
            )
        }
        self._avatars = {
            1: UserAvatar(
                user_id=1, content_type="image/png", data=b"\x89PNG", size_bytes=4
            )
        }
        self._documents = {
            1: [
                UserDocument(
                    document_id=1,
                    user_id=1,
                    title="Resume",
                    content="Lorem ipsum",
                    created_at=datetime(2024, 1, 1),
                    file_size_kb=12.5,
                )
            ]
        }
        self._analytics = {
            1: UserAnalytics(
                user_id=1, login_count=2, document_count=1, total_storage_kb=12.5
            )
        }

    async def get_profile(self, user_id: int) -> UserProfile:
        self.call_counts["get_profile"] += 1
        if user_id not in self._profiles:
            raise UserNotFoundError(user_id)
        return self._profiles[user_id]

    async def get_avatar(self, user_id: int) -> UserAvatar:
        self.call_counts["get_avatar"] += 1
        if user_id not in self._avatars:
            raise AvatarNotFoundError(user_id)
        return self._avatars[user_id]

    async def get_documents(self, user_id: int) -> list[UserDocument]:
        self.call_counts["get_documents"] += 1
        return self._documents.get(user_id, [])

    async def get_analytics(self, user_id: int) -> UserAnalytics:
        self.call_counts["get_analytics"] += 1
        if user_id not in self._analytics:
            raise UserNotFoundError(user_id)
        return self._analytics[user_id]


@pytest.fixture
def fake_real_service() -> FakeUserProfileService:
    return FakeUserProfileService()


@pytest.fixture
def proxy(fake_real_service: FakeUserProfileService) -> LazyUserProfileProxy:
    return LazyUserProfileProxy(real_service=fake_real_service)
