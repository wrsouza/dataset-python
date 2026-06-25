"""Unit tests for TokenBucketRateLimiter, backed by fakeredis."""

from __future__ import annotations

import pytest

from rate_limiting.domain.entities import RateLimitConfig
from rate_limiting.infrastructure.token_bucket_rate_limiter import (
    TokenBucketRateLimiter,
)


@pytest.mark.asyncio
async def test_allows_calls_within_the_configured_budget(
    token_bucket_limiter: TokenBucketRateLimiter, rate_limit_config: RateLimitConfig
) -> None:
    for _ in range(rate_limit_config.max_requests):
        result = await token_bucket_limiter.check_and_consume(
            "client-a", rate_limit_config
        )
        assert result.allowed is True


@pytest.mark.asyncio
async def test_denies_calls_beyond_the_configured_budget(
    token_bucket_limiter: TokenBucketRateLimiter, rate_limit_config: RateLimitConfig
) -> None:
    for _ in range(rate_limit_config.max_requests):
        await token_bucket_limiter.check_and_consume("client-b", rate_limit_config)

    result = await token_bucket_limiter.check_and_consume("client-b", rate_limit_config)

    assert result.allowed is False
    assert result.retry_after_seconds > 0


@pytest.mark.asyncio
async def test_each_client_id_has_an_independent_budget(
    token_bucket_limiter: TokenBucketRateLimiter, rate_limit_config: RateLimitConfig
) -> None:
    for _ in range(rate_limit_config.max_requests):
        await token_bucket_limiter.check_and_consume("client-c", rate_limit_config)

    result_for_other_client = await token_bucket_limiter.check_and_consume(
        "client-d", rate_limit_config
    )

    assert result_for_other_client.allowed is True
