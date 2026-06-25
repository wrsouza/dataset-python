"""Concrete FlyweightFactory backed by Redis for SessionMetadata."""

from __future__ import annotations

import hashlib
import json
import sys
from typing import cast

import redis

from session_cache.domain.entities import SessionMetadata
from session_cache.domain.interfaces import SessionMetadataFactoryABC

# Pre-defined role configurations — intrinsic state per role
_ROLE_DEFINITIONS: dict[str, dict[str, object]] = {
    "admin": {
        "permissions": frozenset(
            [
                "read:all",
                "write:all",
                "delete:all",
                "manage:users",
                "manage:roles",
                "view:metrics",
            ]
        ),
        "max_session_duration": 3600,
        "requires_mfa": True,
        "allowed_ip_ranges": frozenset(["10.0.0.0/8"]),
    },
    "editor": {
        "permissions": frozenset(["read:all", "write:content", "publish:content"]),
        "max_session_duration": 7200,
        "requires_mfa": False,
        "allowed_ip_ranges": frozenset(),
    },
    "viewer": {
        "permissions": frozenset(["read:public", "read:dashboard"]),
        "max_session_duration": 86400,
        "requires_mfa": False,
        "allowed_ip_ranges": frozenset(),
    },
    "moderator": {
        "permissions": frozenset(
            ["read:all", "write:moderation", "delete:comments", "ban:users"]
        ),
        "max_session_duration": 14400,
        "requires_mfa": True,
        "allowed_ip_ranges": frozenset(),
    },
    "analyst": {
        "permissions": frozenset(["read:all", "view:metrics", "export:reports"]),
        "max_session_duration": 28800,
        "requires_mfa": False,
        "allowed_ip_ranges": frozenset(),
    },
}

# Bytes occupied by the intrinsic state inside a SessionMetadata flyweight
_FLYWEIGHT_INTRINSIC_SIZE_BYTES = 512
# Bytes occupied by intrinsic data if duplicated inside each session
_INTRINSIC_PER_SESSION_BYTES = 2048


class RedisSessionMetadataFactory(SessionMetadataFactoryABC):
    """FlyweightFactory that caches SessionMetadata in Redis.

    Uses a two-level cache:
    1. In-process dict (_local_cache) — fastest lookup, avoids Redis round-trips.
    2. Redis hash — persistence across process restarts and multiple workers.

    The cache key is a SHA-256 hash of the role name, making it stable and
    collision-resistant even if role names contain special characters.
    """

    def __init__(self, redis_client: redis.Redis, app_version: str) -> None:
        self._redis = redis_client
        self._app_version = app_version
        self._local_cache: dict[str, SessionMetadata] = {}
        self._redis_key_prefix = "flyweight:session_metadata:"

    def _role_cache_key(self, role: str) -> str:
        """Derive a stable Redis key from the role name."""
        role_hash = hashlib.sha256(role.encode()).hexdigest()[:16]
        return f"{self._redis_key_prefix}{role_hash}"

    def _build_metadata(self, role: str) -> SessionMetadata:
        """Build a new SessionMetadata flyweight for the given role."""
        config = _ROLE_DEFINITIONS.get(
            role,
            {
                "permissions": frozenset(["read:public"]),
                "max_session_duration": 3600,
                "requires_mfa": False,
                "allowed_ip_ranges": frozenset(),
            },
        )
        return SessionMetadata(
            role=role,
            permissions=config["permissions"],  # type: ignore[arg-type]
            app_version=self._app_version,
            max_session_duration=config["max_session_duration"],  # type: ignore[arg-type]
            allowed_ip_ranges=config["allowed_ip_ranges"],  # type: ignore[arg-type]
            requires_mfa=config["requires_mfa"],  # type: ignore[arg-type]
        )

    def _serialize_to_redis(self, metadata: SessionMetadata) -> str:
        """Serialize flyweight to JSON for Redis storage."""
        return json.dumps(
            {
                "role": metadata.role,
                "permissions": list(metadata.permissions),
                "app_version": metadata.app_version,
                "max_session_duration": metadata.max_session_duration,
                "allowed_ip_ranges": list(metadata.allowed_ip_ranges),
                "requires_mfa": metadata.requires_mfa,
            }
        )

    def _deserialize_from_redis(self, data: str) -> SessionMetadata:
        """Reconstruct flyweight from JSON Redis data."""
        obj = json.loads(data)
        return SessionMetadata(
            role=obj["role"],
            permissions=frozenset(obj["permissions"]),
            app_version=obj["app_version"],
            max_session_duration=obj["max_session_duration"],
            allowed_ip_ranges=frozenset(obj["allowed_ip_ranges"]),
            requires_mfa=obj["requires_mfa"],
        )

    def get_or_create(self, role: str) -> SessionMetadata:
        """Return the shared Flyweight for the role — create and cache if missing."""
        # Level 1: in-process cache (same object reference guaranteed)
        if role in self._local_cache:
            return self._local_cache[role]

        # Level 2: Redis cache (shared across workers)
        cache_key = self._role_cache_key(role)
        cached = self._redis.get(cache_key)
        if cached:
            metadata = self._deserialize_from_redis(cast(bytes, cached).decode())
            self._local_cache[role] = metadata
            return metadata

        # Cache miss: build, store in both levels
        metadata = self._build_metadata(role)
        self._redis.set(cache_key, self._serialize_to_redis(metadata), ex=86400)
        self._local_cache[role] = metadata
        return metadata

    def get_flyweight_count(self) -> int:
        """Return the number of unique flyweights in the local cache."""
        return len(self._local_cache)

    def get_cache_stats(self) -> dict[str, int | float]:
        """Return memory economy statistics."""
        n_flyweights = self.get_flyweight_count()
        # We need total sessions from Redis to compute savings
        total_sessions_key = "stats:total_sessions"
        raw = self._redis.get(total_sessions_key)
        total_sessions = int(raw) if raw else 0

        bytes_without = total_sessions * _INTRINSIC_PER_SESSION_BYTES
        bytes_with = (
            n_flyweights * _FLYWEIGHT_INTRINSIC_SIZE_BYTES
            + total_sessions * sys.getsizeof(object())  # just the reference
        )
        saved = max(0, bytes_without - bytes_with)
        pct = (saved / bytes_without * 100) if bytes_without > 0 else 0.0

        return {
            "total_sessions": total_sessions,
            "unique_flyweights": n_flyweights,
            "bytes_without_flyweight": bytes_without,
            "bytes_with_flyweight": bytes_with,
            "bytes_saved": saved,
            "savings_percentage": round(pct, 2),
        }

    def increment_session_counter(self) -> None:
        """Track total sessions for statistics."""
        self._redis.incr("stats:total_sessions")

    def decrement_session_counter(self) -> None:
        """Track session deletion for statistics."""
        self._redis.decr("stats:total_sessions")
