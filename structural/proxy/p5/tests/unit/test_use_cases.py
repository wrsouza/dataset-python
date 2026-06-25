"""Unit tests for EnforceRateLimitUseCase, with a fake RateLimiter."""

from __future__ import annotations

import pytest

from rate_limiting.application.use_cases import EnforceRateLimitUseCase
from rate_limiting.domain.entities import RateLimitConfig, RateLimitResult
from rate_limiting.domain.exceptions import RateLimitExceededError


class _FixedResultRateLimiter:
    """Fake RateLimiter (implements the Protocol) returning a fixed result."""

    def __init__(self, result: RateLimitResult) -> None:
        self._result = result

    async def check_and_consume(
        self, client_id: str, config: RateLimitConfig
    ) -> RateLimitResult:
        return self._result


@pytest.mark.asyncio
async def test_execute_returns_result_when_allowed() -> None:
    config = RateLimitConfig(max_requests=5, window_seconds=10)
    use_case = EnforceRateLimitUseCase(
        rate_limiter=_FixedResultRateLimiter(
            RateLimitResult(allowed=True, remaining=4)
        ),
        config=config,
    )

    result = await use_case.execute("client-x")

    assert result.allowed is True


@pytest.mark.asyncio
async def test_execute_raises_when_denied() -> None:
    config = RateLimitConfig(max_requests=5, window_seconds=10)
    use_case = EnforceRateLimitUseCase(
        rate_limiter=_FixedResultRateLimiter(
            RateLimitResult(allowed=False, remaining=0, retry_after_seconds=2.0)
        ),
        config=config,
    )

    with pytest.raises(RateLimitExceededError) as exc_info:
        await use_case.execute("client-x")

    assert exc_info.value.client_id == "client-x"
    assert exc_info.value.retry_after_seconds == 2.0
