"""Unit tests for RateLimitHandler in isolation (mocked next handler)."""

from __future__ import annotations

from unittest.mock import MagicMock

from validation.domain.entities import APIRequest
from validation.infrastructure.handlers.rate_limit import (
    RateLimitHandler,
    _SlidingWindowCounter,
)


def test_handle_passes_request_when_under_limit() -> None:
    counter = _SlidingWindowCounter(limit=3, window_seconds=60.0)
    handler = RateLimitHandler(counter=counter)
    mock_next = MagicMock(handle=MagicMock(return_value=None))
    handler.set_next(mock_next)
    request = APIRequest(body={}, client_ip="1.2.3.4")

    response = handler.handle(request)

    assert response is None
    mock_next.handle.assert_called_once_with(request)


def test_handle_blocks_request_when_limit_exceeded() -> None:
    counter = _SlidingWindowCounter(limit=1, window_seconds=60.0)
    handler = RateLimitHandler(counter=counter)
    mock_next = MagicMock(handle=MagicMock(return_value=None))
    handler.set_next(mock_next)
    request = APIRequest(body={}, client_ip="9.9.9.9")

    handler.handle(request)  # consumes the only allowed slot
    second_response = handler.handle(request)

    assert second_response is not None
    assert second_response.status_code == 429
    assert second_response.handler_name == "RateLimitHandler"
    mock_next.handle.assert_called_once()


def test_handle_tracks_clients_independently_by_ip() -> None:
    counter = _SlidingWindowCounter(limit=1, window_seconds=60.0)
    handler = RateLimitHandler(counter=counter)
    handler.set_next(MagicMock(handle=MagicMock(return_value=None)))

    first_client = APIRequest(body={}, client_ip="1.1.1.1")
    second_client = APIRequest(body={}, client_ip="2.2.2.2")

    assert handler.handle(first_client) is None
    assert handler.handle(second_client) is None


def test_handle_uses_default_counter_when_none_injected() -> None:
    handler = RateLimitHandler()

    assert handler._counter is not None
