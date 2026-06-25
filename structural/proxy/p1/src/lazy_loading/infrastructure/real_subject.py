"""RealSubject: PostgresUserProfileService.

Performs actual database queries to retrieve user profile data.
This is the "expensive" implementation that the Proxy wraps.
"""

from __future__ import annotations

import asyncpg

from lazy_loading.domain.entities import (
    UserAnalytics,
    UserAvatar,
    UserDocument,
    UserProfile,
)
from lazy_loading.domain.exceptions import AvatarNotFoundError, UserNotFoundError


class PostgresUserProfileService:
    """RealSubject: fetches user data directly from PostgreSQL.

    Each method executes a real query. The Virtual Proxy wraps this class
    to defer these queries until the data is actually needed.
    """

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def get_profile(self, user_id: int) -> UserProfile:
        """Fetch base profile — fast, single-row query."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT user_id, username, email, full_name, created_at, is_active
                FROM users
                WHERE user_id = $1
                """,
                user_id,
            )
        if row is None:
            raise UserNotFoundError(user_id)
        return UserProfile(**dict(row))

    async def get_avatar(self, user_id: int) -> UserAvatar:
        """Fetch avatar binary — potentially large BYTEA column."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT user_id, content_type, data, size_bytes, updated_at
                FROM user_avatars
                WHERE user_id = $1
                """,
                user_id,
            )
        if row is None:
            raise AvatarNotFoundError(user_id)
        return UserAvatar(**dict(row))

    async def get_documents(self, user_id: int) -> list[UserDocument]:
        """Fetch all user documents — may be many rows."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT document_id, user_id, title, content, created_at, file_size_kb
                FROM user_documents
                WHERE user_id = $1
                ORDER BY created_at DESC
                """,
                user_id,
            )
        return [UserDocument(**dict(row)) for row in rows]

    async def get_analytics(self, user_id: int) -> UserAnalytics:
        """Compute analytics — heavy aggregation query."""
        async with self._pool.acquire() as conn:
            # Simulate an expensive aggregation
            row = await conn.fetchrow(
                """
                SELECT
                    u.user_id,
                    COUNT(DISTINCT al.event_id) AS login_count,
                    COUNT(DISTINCT d.document_id) AS document_count,
                    MAX(al.created_at) AS last_login,
                    COALESCE(SUM(d.file_size_kb), 0) AS total_storage_kb,
                    COALESCE(COUNT(DISTINCT al.event_id) * 1.0 +
                             COUNT(DISTINCT d.document_id) * 2.0, 0) AS activity_score
                FROM users u
                LEFT JOIN activity_log al
                    ON al.user_id = u.user_id AND al.event_type = 'login'
                LEFT JOIN user_documents d ON d.user_id = u.user_id
                WHERE u.user_id = $1
                GROUP BY u.user_id
                """,
                user_id,
            )
        if row is None:
            raise UserNotFoundError(user_id)
        return UserAnalytics(**dict(row))
