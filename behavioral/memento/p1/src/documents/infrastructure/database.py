"""Database connection management."""
from __future__ import annotations

import asyncpg

from documents.settings import Settings


async def create_pool(settings: Settings) -> asyncpg.Pool:
    """Create and return an asyncpg connection pool."""
    pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=2,
        max_size=10,
    )
    assert pool is not None
    return pool
