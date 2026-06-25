"""Domain interfaces for the Rate Limiting Proxy project.

``RateLimiter`` is the abstraction that makes the rate-limit *algorithm*
swappable (OCP): TokenBucketRateLimiter and a future SlidingWindowRateLimiter
both implement this Protocol, and RateLimitingProxyServicer depends only on
the Protocol, never on a concrete class (DIP).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from rate_limiting.domain.entities import RateLimitConfig, RateLimitResult


@runtime_checkable
class RateLimiter(Protocol):
    """Strategy for deciding whether a client may perform one more call."""

    async def check_and_consume(
        self, client_id: str, config: RateLimitConfig
    ) -> RateLimitResult:
        """Atomically check the client's budget and consume one unit if allowed.

        Implementations must be safe for concurrent callers sharing the same
        client_id (e.g. via an atomic Redis operation or Lua script).
        """
        ...
