"""Application use case: enforce the rate limit for an incoming call.

This is the only place that turns a denied RateLimitResult into a raised
domain exception — keeping that decision out of both the RateLimiter
implementations (SRP: they only compute allow/deny) and the gRPC servicer
(SRP: it only translates exceptions to gRPC statuses and delegates).
"""

from __future__ import annotations

from rate_limiting.domain.entities import RateLimitConfig, RateLimitResult
from rate_limiting.domain.exceptions import RateLimitExceededError
from rate_limiting.domain.interfaces import RateLimiter


class EnforceRateLimitUseCase:
    """Checks a client's budget and raises if the call should be rejected."""

    def __init__(self, rate_limiter: RateLimiter, config: RateLimitConfig) -> None:
        self._rate_limiter = rate_limiter
        self._config = config

    async def execute(self, client_id: str) -> RateLimitResult:
        """Return the RateLimitResult, raising if the client is over budget."""
        result = await self._rate_limiter.check_and_consume(client_id, self._config)
        if result.denied:
            raise RateLimitExceededError(
                client_id=client_id, retry_after_seconds=result.retry_after_seconds
            )
        return result
