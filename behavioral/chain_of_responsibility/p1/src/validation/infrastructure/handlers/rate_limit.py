"""Rate limiting handler with in-memory sliding window counter."""

from __future__ import annotations

import time
from collections import defaultdict

from validation.domain.entities import APIRequest, APIResponse
from validation.domain.interfaces import RequestHandler


class _SlidingWindowCounter:
    """Thread-unsafe sliding window counter (adequate for single-process demo)."""

    def __init__(self, limit: int, window_seconds: float) -> None:
        self._limit = limit
        self._window = window_seconds
        # Maps key → list of timestamps
        self._timestamps: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        """Return True if the key is within its rate limit, and record the hit."""
        now = time.monotonic()
        cutoff = now - self._window
        hits = self._timestamps[key]

        # Evict expired timestamps to keep memory bounded
        self._timestamps[key] = [ts for ts in hits if ts > cutoff]

        if len(self._timestamps[key]) >= self._limit:
            return False

        self._timestamps[key].append(now)
        return True

    def reset(self, key: str) -> None:
        """Clear the window for testing purposes."""
        self._timestamps.pop(key, None)


# Module-level shared counter — injected via dependency for testability
_default_counter = _SlidingWindowCounter(limit=10, window_seconds=60.0)


class RateLimitHandler(RequestHandler):
    """Enforces per-IP rate limiting using a sliding window.

    SRP: only responsible for rate-limit enforcement.
    DIP: counter is injected, enabling swap for Redis-backed implementation.
    """

    HANDLER_NAME = "RateLimitHandler"

    def __init__(self, counter: _SlidingWindowCounter | None = None) -> None:
        super().__init__()
        self._counter = counter or _default_counter

    def handle(self, request: APIRequest) -> APIResponse | None:
        if not self._counter.is_allowed(request.client_ip):
            return APIResponse.too_many_requests(
                message=(
                    f"Rate limit exceeded for IP {request.client_ip}. "
                    "Try again later."
                ),
                handler_name=self.HANDLER_NAME,
            )
        return self._pass_to_next(request)
