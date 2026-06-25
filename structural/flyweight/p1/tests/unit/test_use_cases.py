"""Tests for session use cases with fakeredis-backed factory/repository."""

from __future__ import annotations

import pytest

from session_cache.application.use_cases import (
    BulkLoginUseCase,
    GetCacheStatsUseCase,
    GetSessionUseCase,
    LoginUseCase,
    SessionNotFoundError,
)
from session_cache.infrastructure.factory import RedisSessionMetadataFactory
from session_cache.infrastructure.repository import RedisSessionRepository


class TestLoginUseCase:
    def test_creates_session_with_shared_flyweight(
        self,
        factory: RedisSessionMetadataFactory,
        repository: RedisSessionRepository,
    ) -> None:
        use_case = LoginUseCase(factory=factory, repository=repository)

        session = use_case.execute(user_id="u1", role="admin")

        assert session.user_id == "u1"
        assert session.role == "admin"
        assert session.token

    def test_two_logins_same_role_share_flyweight(
        self,
        factory: RedisSessionMetadataFactory,
        repository: RedisSessionRepository,
    ) -> None:
        use_case = LoginUseCase(factory=factory, repository=repository)

        session_a = use_case.execute(user_id="u1", role="viewer")
        session_b = use_case.execute(user_id="u2", role="viewer")

        assert session_a.metadata is session_b.metadata
        assert session_a.token != session_b.token


class TestGetSessionUseCase:
    def test_retrieves_existing_session(
        self,
        factory: RedisSessionMetadataFactory,
        repository: RedisSessionRepository,
    ) -> None:
        login_uc = LoginUseCase(factory=factory, repository=repository)
        created = login_uc.execute(user_id="u1", role="editor")

        get_uc = GetSessionUseCase(factory=factory, repository=repository)
        fetched = get_uc.execute(token=created.token)

        assert fetched.user_id == "u1"
        assert fetched.role == "editor"
        assert fetched.metadata is created.metadata

    def test_raises_for_missing_token(
        self,
        factory: RedisSessionMetadataFactory,
        repository: RedisSessionRepository,
    ) -> None:
        get_uc = GetSessionUseCase(factory=factory, repository=repository)

        with pytest.raises(SessionNotFoundError):
            get_uc.execute(token="does-not-exist")

    def test_raises_and_deletes_expired_session(
        self,
        factory: RedisSessionMetadataFactory,
        repository: RedisSessionRepository,
    ) -> None:
        from datetime import datetime, timedelta

        past = datetime.utcnow() - timedelta(hours=2)
        repository.save(
            "expired-token",
            {
                "user_id": "u1",
                "token": "expired-token",
                "role": "viewer",
                "created_at": past.isoformat(),
                "expires_at": past.isoformat(),
                "last_activity": past.isoformat(),
            },
        )

        get_uc = GetSessionUseCase(factory=factory, repository=repository)

        with pytest.raises(SessionNotFoundError):
            get_uc.execute(token="expired-token")

        assert repository.find("expired-token") is None


class TestGetCacheStatsUseCase:
    def test_returns_stats_from_factory(
        self, factory: RedisSessionMetadataFactory
    ) -> None:
        factory.get_or_create("admin")
        factory.increment_session_counter()

        use_case = GetCacheStatsUseCase(factory=factory)
        stats = use_case.execute()

        assert stats.total_sessions == 1
        assert stats.unique_flyweights == 1


class TestBulkLoginUseCase:
    def test_distributes_sessions_across_roles(
        self,
        factory: RedisSessionMetadataFactory,
        repository: RedisSessionRepository,
    ) -> None:
        login_uc = LoginUseCase(factory=factory, repository=repository)
        bulk_uc = BulkLoginUseCase(login_use_case=login_uc)

        distribution = bulk_uc.execute(count=10, roles=["admin", "viewer"])

        assert sum(distribution.values()) == 10
        assert distribution["admin"] == 5
        assert distribution["viewer"] == 5
        # Only 2 unique flyweights regardless of session count
        assert factory.get_flyweight_count() == 2
