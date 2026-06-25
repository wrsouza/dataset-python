"""Redis-backed UserSession repository."""

from __future__ import annotations

import json
from typing import cast

import redis

from session_cache.infrastructure.factory import RedisSessionMetadataFactory


class RedisSessionRepository:
    """Persists UserSession (extrinsic state only) in Redis.

    The Flyweight (SessionMetadata) is NOT serialized per session —
    only the role key is stored, allowing reconstruction via the factory.
    This is the core memory economy of the Flyweight pattern.
    """

    _KEY_PREFIX = "session:"

    def __init__(
        self,
        redis_client: redis.Redis,
        factory: RedisSessionMetadataFactory,
    ) -> None:
        self._redis = redis_client
        self._factory = factory

    def _session_key(self, token: str) -> str:
        return f"{self._KEY_PREFIX}{token}"

    def save(self, token: str, session_data: dict[str, object]) -> None:
        ttl = 86400  # 24 hours default
        self._redis.setex(
            self._session_key(token),
            ttl,
            json.dumps(session_data),
        )

    def find(self, token: str) -> dict[str, object] | None:
        raw = self._redis.get(self._session_key(token))
        if raw is None:
            return None
        return cast(dict[str, object], json.loads(cast(bytes, raw).decode()))

    def delete(self, token: str) -> None:
        self._redis.delete(self._session_key(token))

    def count_active(self) -> int:
        keys = self._redis.keys(f"{self._KEY_PREFIX}*")
        return len(keys)
