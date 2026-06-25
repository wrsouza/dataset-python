"""Domain entities for the Rate Limiting Proxy project.

Plain dataclasses, no dependency on gRPC, Redis, or any infrastructure
concern — they describe the rate-limiting domain in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RateLimitConfig:
    """Configuration for how many requests a client may make in a window.

    ``max_requests`` per ``window_seconds`` defines the budget; the concrete
    algorithm (token bucket, sliding window, ...) decides how that budget is
    enforced over time.
    """

    max_requests: int
    window_seconds: int

    def __post_init__(self) -> None:
        if self.max_requests <= 0:
            raise ValueError("max_requests must be a positive integer")
        if self.window_seconds <= 0:
            raise ValueError("window_seconds must be a positive integer")


@dataclass(frozen=True, slots=True)
class RateLimitResult:
    """Outcome of evaluating a rate-limit check for one client + key."""

    allowed: bool
    remaining: int
    retry_after_seconds: float = 0.0

    @property
    def denied(self) -> bool:
        """True when the caller has exhausted its budget."""
        return not self.allowed
