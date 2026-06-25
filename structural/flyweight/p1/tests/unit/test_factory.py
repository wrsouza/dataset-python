"""Tests for RedisSessionMetadataFactory — verifies Flyweight sharing."""

from __future__ import annotations

from session_cache.infrastructure.factory import RedisSessionMetadataFactory


def test_get_or_create_returns_same_instance_for_same_role(
    factory: RedisSessionMetadataFactory,
) -> None:
    """Core Flyweight guarantee: same role → same object reference."""
    metadata_a = factory.get_or_create("admin")
    metadata_b = factory.get_or_create("admin")

    assert metadata_a is metadata_b


def test_get_or_create_returns_different_instance_for_different_roles(
    factory: RedisSessionMetadataFactory,
) -> None:
    metadata_admin = factory.get_or_create("admin")
    metadata_viewer = factory.get_or_create("viewer")

    assert metadata_admin is not metadata_viewer


def test_flyweight_is_frozen(factory: RedisSessionMetadataFactory) -> None:
    """SessionMetadata must be immutable."""
    import dataclasses

    import pytest

    metadata = factory.get_or_create("editor")

    with pytest.raises(dataclasses.FrozenInstanceError):
        metadata.role = "hacked"  # type: ignore[misc]


def test_known_roles_have_expected_permissions(
    factory: RedisSessionMetadataFactory,
) -> None:
    admin = factory.get_or_create("admin")
    viewer = factory.get_or_create("viewer")

    assert "manage:users" in admin.permissions
    assert "manage:users" not in viewer.permissions
    assert admin.requires_mfa is True
    assert viewer.requires_mfa is False


def test_unknown_role_gets_default_permissions(
    factory: RedisSessionMetadataFactory,
) -> None:
    metadata = factory.get_or_create("totally_unknown_role")

    assert metadata.permissions == frozenset(["read:public"])


def test_get_flyweight_count_reflects_unique_roles(
    factory: RedisSessionMetadataFactory,
) -> None:
    initial = factory.get_flyweight_count()

    factory.get_or_create("admin")
    factory.get_or_create("admin")  # same role — no new flyweight
    assert factory.get_flyweight_count() == initial + 1

    factory.get_or_create("editor")
    assert factory.get_flyweight_count() == initial + 2


def test_redis_cache_survives_local_cache_eviction(
    factory: RedisSessionMetadataFactory,
) -> None:
    """A second factory (new process) rebuilds equal intrinsic state from Redis."""
    first = factory.get_or_create("moderator")

    second_factory = RedisSessionMetadataFactory(
        redis_client=factory._redis,  # noqa: SLF001 - test introspection
        app_version="1.0.0-test",
    )
    second = second_factory.get_or_create("moderator")

    # Different objects (different process), but equal intrinsic state
    assert first is not second
    assert first == second


def test_get_cache_stats_reports_economy(factory: RedisSessionMetadataFactory) -> None:
    factory.get_or_create("admin")
    factory.increment_session_counter()
    factory.increment_session_counter()

    stats = factory.get_cache_stats()

    assert stats["total_sessions"] == 2
    assert stats["unique_flyweights"] == 1
    assert stats["bytes_saved"] >= 0
