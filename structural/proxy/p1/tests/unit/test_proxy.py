"""Unit tests for LazyUserProfileProxy — the core of the Virtual Proxy pattern."""

from __future__ import annotations

import pytest

from lazy_loading.domain.exceptions import AvatarNotFoundError, UserNotFoundError
from lazy_loading.infrastructure.proxy import LazyUserProfileProxy
from tests.conftest import FakeUserProfileService


async def test_get_profile_delegates_to_real_service_on_first_call(
    proxy: LazyUserProfileProxy, fake_real_service: FakeUserProfileService
) -> None:
    profile = await proxy.get_profile(1)

    assert profile.username == "alice"
    assert fake_real_service.call_counts["get_profile"] == 1


async def test_get_profile_uses_cache_on_second_call(
    proxy: LazyUserProfileProxy, fake_real_service: FakeUserProfileService
) -> None:
    await proxy.get_profile(1)
    await proxy.get_profile(1)

    assert fake_real_service.call_counts["get_profile"] == 1  # real service hit once


async def test_get_profile_raises_for_unknown_user(
    proxy: LazyUserProfileProxy,
) -> None:
    with pytest.raises(UserNotFoundError):
        await proxy.get_profile(999)


async def test_get_avatar_caches_after_first_load(
    proxy: LazyUserProfileProxy, fake_real_service: FakeUserProfileService
) -> None:
    await proxy.get_avatar(1)
    await proxy.get_avatar(1)
    await proxy.get_avatar(1)

    assert fake_real_service.call_counts["get_avatar"] == 1


async def test_get_avatar_raises_for_missing_avatar(
    proxy: LazyUserProfileProxy,
) -> None:
    with pytest.raises(AvatarNotFoundError):
        await proxy.get_avatar(2)  # user 2 has no avatar in the fake


async def test_get_documents_caches_after_first_load(
    proxy: LazyUserProfileProxy, fake_real_service: FakeUserProfileService
) -> None:
    first = await proxy.get_documents(1)
    second = await proxy.get_documents(1)

    assert first == second
    assert fake_real_service.call_counts["get_documents"] == 1


async def test_get_analytics_triggers_expensive_query_once(
    proxy: LazyUserProfileProxy, fake_real_service: FakeUserProfileService
) -> None:
    await proxy.get_analytics(1)
    await proxy.get_analytics(1)

    assert fake_real_service.call_counts["get_analytics"] == 1


async def test_load_stats_track_loads_and_cache_hits(
    proxy: LazyUserProfileProxy,
) -> None:
    await proxy.get_profile(1)
    await proxy.get_profile(1)
    await proxy.get_profile(1)

    stats = proxy.get_load_stats()

    assert stats.profile_loads == 1
    assert stats.profile_cache_hits == 2
    assert stats.total_loads == 1
    assert stats.total_cache_hits == 2


async def test_invalidate_clears_cache_for_user(
    proxy: LazyUserProfileProxy, fake_real_service: FakeUserProfileService
) -> None:
    await proxy.get_profile(1)
    proxy.invalidate(1)
    await proxy.get_profile(1)

    assert fake_real_service.call_counts["get_profile"] == 2  # reloaded after evict


async def test_different_users_are_cached_independently(
    proxy: LazyUserProfileProxy, fake_real_service: FakeUserProfileService
) -> None:
    await proxy.get_documents(1)
    documents_user_2 = await proxy.get_documents(2)

    assert documents_user_2 == []
    assert fake_real_service.call_counts["get_documents"] == 2
