"""Application use cases for Session Token Cache."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from session_cache.domain.entities import CacheStats, SessionMetadata, UserSession
from session_cache.domain.interfaces import (
    SessionMetadataFactoryABC,
    SessionRepositoryProtocol,
)


class SessionNotFoundError(Exception):
    """Raised when a session token does not exist or has expired."""

    def __init__(self, token: str) -> None:
        super().__init__(f"Session not found or expired: {token!r}")
        self.token = token


class LoginUseCase:
    """Create a new session, reusing the Flyweight for the user's role.

    SRP: only responsible for session creation.
    DIP: depends on abstractions (factory + repository), not concrete Redis.
    """

    def __init__(
        self,
        factory: SessionMetadataFactoryABC,
        repository: SessionRepositoryProtocol,
    ) -> None:
        self._factory = factory
        self._repository = repository

    def execute(self, user_id: str, role: str) -> UserSession:
        """Create a session, fetching the shared Flyweight for the role."""
        # The factory returns the SAME object for the same role — core Flyweight
        metadata: SessionMetadata = self._factory.get_or_create(role)  # type: ignore[assignment]

        now = datetime.utcnow()
        session = UserSession(
            user_id=user_id,
            token=secrets.token_urlsafe(32),
            metadata=metadata,
            created_at=now,
            expires_at=now + timedelta(seconds=metadata.max_session_duration),
            last_activity=now,
        )

        self._repository.save(session.token, session.to_dict())
        return session


class GetSessionUseCase:
    """Retrieve and validate a session by token.

    Reconstructs UserSession by loading extrinsic state from Redis and
    re-attaching the shared Flyweight via the factory — no duplication.
    """

    def __init__(
        self,
        factory: SessionMetadataFactoryABC,
        repository: SessionRepositoryProtocol,
    ) -> None:
        self._factory = factory
        self._repository = repository

    def execute(self, token: str) -> UserSession:
        data = self._repository.find(token)
        if data is None:
            raise SessionNotFoundError(token)

        # Reconstruct the Flyweight by role — same object as all other sessions
        metadata: SessionMetadata = self._factory.get_or_create(str(data["role"]))  # type: ignore[assignment]

        session = UserSession(
            user_id=str(data["user_id"]),
            token=str(data["token"]),
            metadata=metadata,
            created_at=datetime.fromisoformat(str(data["created_at"])),
            expires_at=datetime.fromisoformat(str(data["expires_at"])),
            last_activity=datetime.fromisoformat(str(data["last_activity"])),
        )

        if session.is_expired():
            self._repository.delete(token)
            raise SessionNotFoundError(token)

        return session


class GetCacheStatsUseCase:
    """Compute and return memory economy statistics for the Flyweight cache."""

    def __init__(self, factory: SessionMetadataFactoryABC) -> None:
        self._factory = factory

    def execute(self) -> CacheStats:
        raw_stats = self._factory.get_cache_stats()
        return CacheStats(
            total_sessions=int(raw_stats["total_sessions"]),
            unique_flyweights=int(raw_stats["unique_flyweights"]),
            roles_cached=[],  # populated separately
            estimated_bytes_without_flyweight=int(raw_stats["bytes_without_flyweight"]),
            estimated_bytes_with_flyweight=int(raw_stats["bytes_with_flyweight"]),
        )


class BulkLoginUseCase:
    """Demonstrate Flyweight economy by creating many sessions across N roles."""

    def __init__(self, login_use_case: LoginUseCase) -> None:
        self._login = login_use_case

    def execute(self, count: int, roles: list[str]) -> dict[str, int]:
        """Create `count` sessions spread across roles; return role distribution."""
        distribution: dict[str, int] = dict.fromkeys(roles, 0)
        for i in range(count):
            role = roles[i % len(roles)]
            self._login.execute(user_id=f"user_{i:06d}", role=role)
            distribution[role] += 1
        return distribution
