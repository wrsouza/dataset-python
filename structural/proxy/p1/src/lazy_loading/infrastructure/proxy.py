"""Proxy: LazyUserProfileProxy — Virtual Proxy implementation.

Intercepts calls to the UserProfileService and loads data only when
actually requested, caching results locally to avoid repeated DB hits.

Pattern roles:
  - Subject:     UserProfileService (Protocol in domain/interfaces.py)
  - RealSubject: PostgresUserProfileService (infrastructure/real_subject.py)
  - Proxy:       LazyUserProfileProxy (this file)
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

# Sentinel to distinguish "not yet loaded" from a None result
_NOT_LOADED = object()


class LazyUserProfileProxy:
    """Virtual Proxy that defers DB calls until the data is accessed.

    The proxy maintains a per-user cache. Each attribute group (profile,
    avatar, documents, analytics) is fetched from Postgres exactly once;
    subsequent accesses are served from the in-memory cache.

    Clients code against UserProfileService (the Protocol), so they are
    completely unaware whether they hold a Proxy or the Real object.
    """

    def __init__(self, real_service: UserProfileService) -> None:
        self._real = real_service
        # Per-user caches: user_id → loaded value
        self._profile_cache: dict[int, UserProfile] = {}
        self._avatar_cache: dict[int, UserAvatar] = {}
        self._documents_cache: dict[int, list[UserDocument]] = {}
        self._analytics_cache: dict[int, UserAnalytics] = {}
        # Load counters for observability
        self._stats = LoadStats()

    async def get_profile(self, user_id: int) -> UserProfile:
        """Return cached profile or load from DB on first access."""
        if user_id in self._profile_cache:
            self._stats.profile_cache_hits += 1
            return self._profile_cache[user_id]

        self._stats.profile_loads += 1
        profile = await self._real.get_profile(user_id)
        self._profile_cache[user_id] = profile
        return profile

    async def get_avatar(self, user_id: int) -> UserAvatar:
        """Return cached avatar or load from DB on first access."""
        if user_id in self._avatar_cache:
            self._stats.avatar_cache_hits += 1
            return self._avatar_cache[user_id]

        self._stats.avatar_loads += 1
        avatar = await self._real.get_avatar(user_id)
        self._avatar_cache[user_id] = avatar
        return avatar

    async def get_documents(self, user_id: int) -> list[UserDocument]:
        """Return cached documents or load from DB on first access."""
        if user_id in self._documents_cache:
            self._stats.documents_cache_hits += 1
            return self._documents_cache[user_id]

        self._stats.documents_loads += 1
        documents = await self._real.get_documents(user_id)
        self._documents_cache[user_id] = documents
        return documents

    async def get_analytics(self, user_id: int) -> UserAnalytics:
        """Return cached analytics or trigger expensive aggregation once."""
        if user_id in self._analytics_cache:
            self._stats.analytics_cache_hits += 1
            return self._analytics_cache[user_id]

        self._stats.analytics_loads += 1
        analytics = await self._real.get_analytics(user_id)
        self._analytics_cache[user_id] = analytics
        return analytics

    def get_load_stats(self) -> LoadStats:
        """Return accumulated load vs. cache-hit statistics."""
        return self._stats

    def invalidate(self, user_id: int) -> None:
        """Evict all cached data for a user (call after writes)."""
        self._profile_cache.pop(user_id, None)
        self._avatar_cache.pop(user_id, None)
        self._documents_cache.pop(user_id, None)
        self._analytics_cache.pop(user_id, None)
