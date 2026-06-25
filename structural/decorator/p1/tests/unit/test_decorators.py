"""Unit tests for individual decorators and the composed chain.

Tests verify:
  1. Each decorator in isolation (SRP verification)
  2. Decorators composed in a chain (Decorator pattern verification)
  3. Order of decorators affects behaviour
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest

from middleware.application.use_cases import (
    BaseRequestHandler,
    build_full_pipeline,
    build_minimal_pipeline,
    build_public_pipeline,
)
from middleware.domain.entities import (
    AuthenticationError,
    ConcreteHTTPRequest,
    ConcreteHTTPResponse,
    RateLimitExceededError,
)
from middleware.domain.interfaces import RequestHandler, RequestHandlerDecorator
from middleware.infrastructure.decorators import (
    AuthDecorator,
    CacheDecorator,
    CompressionDecorator,
    LoggingDecorator,
    RateLimitDecorator,
)


def make_request(**kwargs: object) -> ConcreteHTTPRequest:
    defaults = {
        "method": "GET",
        "path": "/test",
        "headers": {"Authorization": "Bearer valid-jwt-token"},
        "client_ip": "10.0.0.1",
    }
    defaults.update(kwargs)  # type: ignore[arg-type]
    return ConcreteHTTPRequest(**defaults)  # type: ignore[arg-type]


def make_ok_response(body: bytes = b"hello") -> ConcreteHTTPResponse:
    return ConcreteHTTPResponse(status_code=200, body=body)


# ── Base handler ──────────────────────────────────────────────────────────────


class TestBaseRequestHandler:
    def test_returns_200_with_json_body(self) -> None:
        handler = BaseRequestHandler()
        request = make_request()
        response = handler.handle(request)
        assert response.status_code == 200
        assert b"/test" in response.body

    def test_reflects_method_in_body(self) -> None:
        handler = BaseRequestHandler()
        request = make_request(method="POST")
        response = handler.handle(request)
        assert b"POST" in response.body


# ── RequestHandlerDecorator ABC ───────────────────────────────────────────────


class TestDecoratorABC:
    def test_default_implementation_delegates(self) -> None:
        """Decorator ABC must delegate to wrapped handler by default."""
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = make_ok_response()

        # Use the concrete ABC subclass directly (no override)
        class PassThroughDecorator(RequestHandlerDecorator):
            pass

        decorator = PassThroughDecorator(inner)
        request = make_request()
        decorator.handle(request)
        inner.handle.assert_called_once_with(request)


# ── Auth Decorator ────────────────────────────────────────────────────────────


class TestAuthDecorator:
    def test_valid_token_passes_through(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = make_ok_response()
        decorator = AuthDecorator(inner)
        request = make_request(headers={"Authorization": "Bearer valid-jwt-token"})
        decorator.handle(request)
        inner.handle.assert_called_once()

    def test_injects_user_id_header(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = make_ok_response()
        decorator = AuthDecorator(inner)
        request = make_request(headers={"Authorization": "Bearer valid-jwt-token"})
        decorator.handle(request)
        assert request.headers.get("X-User-Id") == "user-42"

    def test_missing_token_raises(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        decorator = AuthDecorator(inner)
        request = make_request(headers={})
        with pytest.raises(AuthenticationError):
            decorator.handle(request)

    def test_invalid_token_raises(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        decorator = AuthDecorator(inner)
        request = make_request(headers={"Authorization": "Bearer bad-token"})
        with pytest.raises(AuthenticationError):
            decorator.handle(request)


# ── Rate Limit Decorator ──────────────────────────────────────────────────────


class TestRateLimitDecorator:
    def test_allows_requests_under_limit(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = make_ok_response()
        decorator = RateLimitDecorator(inner, max_requests_per_minute=5)
        request = make_request()
        for _ in range(5):
            decorator.handle(request)
        assert inner.handle.call_count == 5

    def test_blocks_request_over_limit(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = make_ok_response()
        decorator = RateLimitDecorator(inner, max_requests_per_minute=3)
        request = make_request()
        for _ in range(3):
            decorator.handle(request)
        with pytest.raises(RateLimitExceededError):
            decorator.handle(request)

    def test_different_ips_have_separate_limits(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = make_ok_response()
        decorator = RateLimitDecorator(inner, max_requests_per_minute=2)
        req_a = make_request(client_ip="1.1.1.1")
        req_b = make_request(client_ip="2.2.2.2")
        decorator.handle(req_a)
        decorator.handle(req_a)
        # IP A is at limit, IP B should still work
        with pytest.raises(RateLimitExceededError):
            decorator.handle(req_a)
        decorator.handle(req_b)  # must not raise


# ── Logging Decorator ─────────────────────────────────────────────────────────


class TestLoggingDecorator:
    def test_passes_response_through(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = make_ok_response(b"data")
        decorator = LoggingDecorator(inner)
        response = decorator.handle(make_request())
        assert response.status_code == 200
        assert response.body == b"data"

    def test_records_processing_time(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = make_ok_response()
        decorator = LoggingDecorator(inner)
        response = decorator.handle(make_request())
        assert response.processing_time_ms >= 0


# ── Cache Decorator ───────────────────────────────────────────────────────────


class TestCacheDecorator:
    def test_caches_get_response(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = make_ok_response(b"cached body")
        decorator = CacheDecorator(inner, ttl_seconds=60)
        request = make_request()
        decorator.handle(request)
        decorator.handle(request)
        # Inner handler called only once; second call served from cache
        assert inner.handle.call_count == 1

    def test_does_not_cache_post(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = make_ok_response()
        decorator = CacheDecorator(inner, ttl_seconds=60)
        for _ in range(3):
            decorator.handle(make_request(method="POST"))
        assert inner.handle.call_count == 3

    def test_cache_hit_sets_header(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = make_ok_response()
        decorator = CacheDecorator(inner, ttl_seconds=60)
        request = make_request()
        decorator.handle(request)
        response = decorator.handle(request)
        assert response.headers.get("X-Cache") == "HIT"

    def test_invalidate_clears_cache(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = make_ok_response()
        decorator = CacheDecorator(inner, ttl_seconds=60)
        request = make_request()
        decorator.handle(request)
        assert decorator.cached_count == 1
        decorator.invalidate()
        assert decorator.cached_count == 0

    def test_expired_cache_re_fetches(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = make_ok_response()
        decorator = CacheDecorator(inner, ttl_seconds=0)  # expires immediately
        request = make_request()
        decorator.handle(request)
        time.sleep(0.01)
        decorator.handle(request)
        assert inner.handle.call_count == 2


# ── Compression Decorator ─────────────────────────────────────────────────────


class TestCompressionDecorator:
    def test_compresses_large_response_when_accepted(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        large_body = b"x" * 2048
        inner.handle.return_value = ConcreteHTTPResponse(
            status_code=200, body=large_body
        )
        decorator = CompressionDecorator(inner)
        request = make_request(
            headers={"Authorization": "Bearer valid-jwt-token", "Accept-Encoding": "gzip"}
        )
        response = decorator.handle(request)
        assert response.headers.get("Content-Encoding") == "gzip"
        # Compressed body is smaller
        assert len(response.body) < len(large_body)

    def test_does_not_compress_small_response(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = ConcreteHTTPResponse(status_code=200, body=b"small")
        decorator = CompressionDecorator(inner)
        request = make_request(
            headers={"Authorization": "Bearer valid-jwt-token", "Accept-Encoding": "gzip"}
        )
        response = decorator.handle(request)
        assert "Content-Encoding" not in response.headers

    def test_skips_compression_without_accept_encoding(self) -> None:
        inner = MagicMock(spec=RequestHandler)
        inner.handle.return_value = ConcreteHTTPResponse(
            status_code=200, body=b"x" * 2048
        )
        decorator = CompressionDecorator(inner)
        request = make_request(headers={"Authorization": "Bearer valid-jwt-token"})
        response = decorator.handle(request)
        assert "Content-Encoding" not in response.headers


# ── Chain composition ─────────────────────────────────────────────────────────


class TestDecoratorChain:
    def test_full_pipeline_processes_valid_request(self) -> None:
        pipeline = build_full_pipeline()
        request = make_request(headers={"Authorization": "Bearer valid-jwt-token"})
        response = pipeline.handle(request)
        assert response.status_code == 200

    def test_full_pipeline_rejects_unauthenticated(self) -> None:
        pipeline = build_full_pipeline()
        request = make_request(headers={})
        with pytest.raises(AuthenticationError):
            pipeline.handle(request)

    def test_public_pipeline_works_without_auth(self) -> None:
        pipeline = build_public_pipeline()
        request = make_request(headers={})  # no auth header
        response = pipeline.handle(request)
        assert response.status_code == 200

    def test_minimal_pipeline_returns_ok(self) -> None:
        pipeline = build_minimal_pipeline()
        response = pipeline.handle(make_request())
        assert response.status_code == 200

    def test_chain_order_auth_before_ratelimit(self) -> None:
        """Auth failure should short-circuit before rate limit is checked."""
        inner = BaseRequestHandler()
        rate_limit = RateLimitDecorator(inner, max_requests_per_minute=1)
        auth = AuthDecorator(rate_limit)

        bad_request = make_request(headers={"Authorization": "Bearer bad"})
        with pytest.raises(AuthenticationError):
            auth.handle(bad_request)
        # Rate limit counter must NOT be incremented for unauthenticated request
        good_request = make_request(headers={"Authorization": "Bearer valid-jwt-token"})
        response = auth.handle(good_request)
        assert response.status_code == 200
