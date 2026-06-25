"""Application use cases — depend only on the UserProfileService Protocol.

Use cases never import PostgresUserProfileService or LazyUserProfileProxy
directly. They receive the service via constructor injection (DIP).
"""

from __future__ import annotations

from lazy_loading.domain.entities import (
    LoadStats,
    UserAnalytics,
    UserAvatar,
    UserDocument,
    UserProfile,
)
from lazy_loading.domain.interfaces import UserProfileService
from lazy_loading.infrastructure.proxy import LazyUserProfileProxy


class GetUserProfileUseCase:
    """Retrieve base profile data for a user."""

    def __init__(self, service: UserProfileService) -> None:
        self._service = service

    async def execute(self, user_id: int) -> UserProfile:
        return await self._service.get_profile(user_id)


class GetUserAvatarUseCase:
    """Retrieve avatar for a user — triggers lazy load if not cached."""

    def __init__(self, service: UserProfileService) -> None:
        self._service = service

    async def execute(self, user_id: int) -> UserAvatar:
        return await self._service.get_avatar(user_id)


class GetUserDocumentsUseCase:
    """Retrieve all documents for a user — triggers lazy load if not cached."""

    def __init__(self, service: UserProfileService) -> None:
        self._service = service

    async def execute(self, user_id: int) -> list[UserDocument]:
        return await self._service.get_documents(user_id)


class GetUserAnalyticsUseCase:
    """Retrieve analytics — triggers expensive aggregation once, then cache."""

    def __init__(self, service: UserProfileService) -> None:
        self._service = service

    async def execute(self, user_id: int) -> UserAnalytics:
        return await self._service.get_analytics(user_id)


class GetLoadStatsUseCase:
    """Return proxy load statistics — only works when service is a proxy."""

    def __init__(self, proxy: LazyUserProfileProxy) -> None:
        # This use case explicitly requires the Proxy to read stats.
        # The stats endpoint is an infrastructure concern, not a domain use case.
        self._proxy = proxy

    def execute(self) -> LoadStats:
        return self._proxy.get_load_stats()
