"""Shared fixtures.

Uses fakeredis's async client so unit/integration tests exercise the real
Lua-script token bucket logic without requiring a real Redis instance.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from fakeredis import aioredis as fake_aioredis

from rate_limiting.domain.entities import RateLimitConfig
from rate_limiting.infrastructure.real_data_service import RealDataServiceServicer
from rate_limiting.infrastructure.token_bucket_rate_limiter import (
    TokenBucketRateLimiter,
)


@pytest_asyncio.fixture
async def fake_redis_client() -> AsyncIterator[fake_aioredis.FakeRedis]:
    client = fake_aioredis.FakeRedis()
    yield client
    await client.aclose()


@pytest.fixture
def rate_limit_config() -> RateLimitConfig:
    return RateLimitConfig(max_requests=3, window_seconds=10)


@pytest_asyncio.fixture
async def token_bucket_limiter(
    fake_redis_client: fake_aioredis.FakeRedis,
) -> TokenBucketRateLimiter:
    return TokenBucketRateLimiter(redis_client=fake_redis_client)


@pytest.fixture
def real_servicer() -> RealDataServiceServicer:
    return RealDataServiceServicer()
