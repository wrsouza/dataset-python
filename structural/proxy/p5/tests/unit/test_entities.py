"""Unit tests for domain entities."""

from __future__ import annotations

import pytest

from rate_limiting.domain.entities import RateLimitConfig, RateLimitResult


def test_rate_limit_config_accepts_valid_values() -> None:
    config = RateLimitConfig(max_requests=5, window_seconds=10)

    assert config.max_requests == 5
    assert config.window_seconds == 10


@pytest.mark.parametrize(
    ("max_requests", "window_seconds"), [(0, 10), (-1, 10), (5, 0), (5, -1)]
)
def test_rate_limit_config_rejects_invalid_values(
    max_requests: int, window_seconds: int
) -> None:
    with pytest.raises(ValueError, match="must be a positive integer"):
        RateLimitConfig(max_requests=max_requests, window_seconds=window_seconds)


def test_rate_limit_result_denied_is_inverse_of_allowed() -> None:
    allowed_result = RateLimitResult(allowed=True, remaining=2)
    denied_result = RateLimitResult(allowed=False, remaining=0, retry_after_seconds=1.5)

    assert allowed_result.denied is False
    assert denied_result.denied is True
