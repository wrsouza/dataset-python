"""Unit tests for RateLimitingProxyServicer with a mocked RealSubject.

Verifies the core Proxy behaviour: calls within budget are delegated to the
real servicer untouched; calls beyond budget never reach the real servicer
and get RESOURCE_EXHAUSTED instead.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import grpc
import pytest

from rate_limiting.domain.entities import RateLimitConfig
from rate_limiting.infrastructure.generated import service_pb2
from rate_limiting.infrastructure.rate_limiting_proxy import RateLimitingProxyServicer
from rate_limiting.infrastructure.token_bucket_rate_limiter import (
    TokenBucketRateLimiter,
)


@pytest.fixture
def mock_real_servicer() -> MagicMock:
    mock = MagicMock()
    mock.GetData.return_value = service_pb2.DataResponse(
        key="greeting", value="mocked value", served_at_unix_ms=123
    )
    return mock


@pytest.fixture
def mock_context() -> MagicMock:
    return MagicMock(spec=grpc.ServicerContext)


def test_delegates_to_real_servicer_when_within_budget(
    mock_real_servicer: MagicMock,
    mock_context: MagicMock,
    token_bucket_limiter: TokenBucketRateLimiter,
    rate_limit_config: RateLimitConfig,
) -> None:
    proxy = RateLimitingProxyServicer(
        real_servicer=mock_real_servicer,
        rate_limiter=token_bucket_limiter,
        config=rate_limit_config,
    )
    request = service_pb2.DataRequest(client_id="client-1", key="greeting")

    response = proxy.GetData(request, mock_context)

    mock_real_servicer.GetData.assert_called_once_with(request, mock_context)
    assert response.value == "mocked value"
    mock_context.set_code.assert_not_called()


def test_returns_resource_exhausted_when_budget_is_exceeded(
    mock_real_servicer: MagicMock,
    mock_context: MagicMock,
    token_bucket_limiter: TokenBucketRateLimiter,
    rate_limit_config: RateLimitConfig,
) -> None:
    proxy = RateLimitingProxyServicer(
        real_servicer=mock_real_servicer,
        rate_limiter=token_bucket_limiter,
        config=rate_limit_config,
    )
    request = service_pb2.DataRequest(client_id="client-2", key="greeting")

    for _ in range(rate_limit_config.max_requests):
        proxy.GetData(request, mock_context)
    mock_real_servicer.reset_mock()
    mock_context.reset_mock()

    proxy.GetData(request, mock_context)

    mock_real_servicer.GetData.assert_not_called()
    mock_context.set_code.assert_called_once_with(grpc.StatusCode.RESOURCE_EXHAUSTED)
