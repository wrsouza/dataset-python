"""Concrete Decorator implementations for the HTTP Middleware Pipeline.

Each decorator adds exactly one cross-cutting concern (SRP).
New behaviours are added by creating new decorators (OCP).
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from collections import defaultdict
from typing import Any

from middleware.domain.entities import (
    AuthenticationError,
    AuthToken,
    ConcreteHTTPRequest,
    ConcreteHTTPResponse,
    RateLimitExceededError,
)
from middleware.domain.interfaces import RequestHandlerDecorator

logger = logging.getLogger(__name__)

# ── Auth ──────────────────────────────────────────────────────────────────────

_FAKE_VALID_TOKEN = "Bearer valid-jwt-token"
_FAKE_TOKEN_PAYLOAD = AuthToken(
    user_id="user-42",
    roles=["read", "write"],
    expires_at=time.time() + 3600,
)


class AuthDecorator(RequestHandlerDecorator):
    """Validates the Authorization header before passing the request downstream.

    Adds `X-User-Id` and `X-User-Roles` to the request headers so inner
    handlers can access identity without re-parsing the token.
    """

    def handle(self, request: ConcreteHTTPRequest) -> ConcreteHTTPResponse:
        auth_header = request.headers.get("Authorization", "")
        token = self._validate_token(auth_header)
        # Propagate identity in headers (avoids coupling downstream to JWT logic)
        request.headers["X-User-Id"] = token.user_id
        request.headers["X-User-Roles"] = ",".join(token.roles)
        return self._wrapped.handle(request)

    def _validate_token(self, header: str) -> AuthToken:
        if not header:
            raise AuthenticationError("Authorization header missing")
        if header != _FAKE_VALID_TOKEN:
            raise AuthenticationError(f"Invalid token: {header[:20]}...")
        return _FAKE_TOKEN_PAYLOAD


# ── Rate Limit ────────────────────────────────────────────────────────────────


class RateLimitDecorator(RequestHandlerDecorator):
    """Enforces a maximum number of requests per minute per client IP.

    Uses an in-memory sliding window. In production, replace with Redis.
    """

    def __init__(
        self,
        wrapped: Any,
        max_requests_per_minute: int = 60,
    ) -> None:
        super().__init__(wrapped)
        self._limit = max_requests_per_minute
        # Map client_ip -> list of request timestamps in the last 60 s
        self._windows: dict[str, list[float]] = defaultdict(list)

    def handle(self, request: ConcreteHTTPRequest) -> ConcreteHTTPResponse:
        self._enforce_limit(request.client_ip)
        return self._wrapped.handle(request)

    def _enforce_limit(self, client_ip: str) -> None:
        now = time.time()
        window = self._windows[client_ip]
        # Keep only timestamps within the last 60 seconds
        self._windows[client_ip] = [t for t in window if now - t < 60]
        if len(self._windows[client_ip]) >= self._limit:
            raise RateLimitExceededError(client_ip, self._limit)
        self._windows[client_ip].append(now)


# ── Logging ───────────────────────────────────────────────────────────────────


class LoggingDecorator(RequestHandlerDecorator):
    """Logs structured request/response metadata without touching business logic."""

    def handle(self, request: ConcreteHTTPRequest) -> ConcreteHTTPResponse:
        logger.info(
            json.dumps(
                {
                    "event": "request",
                    "request_id": request.request_id,
                    "method": request.method,
                    "path": request.path,
                    "client_ip": request.client_ip,
                }
            )
        )
        start = time.perf_counter()
        response = self._wrapped.handle(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.processing_time_ms = elapsed_ms
        logger.info(
            json.dumps(
                {
                    "event": "response",
                    "request_id": request.request_id,
                    "status_code": response.status_code,
                    "elapsed_ms": round(elapsed_ms, 2),
                }
            )
        )
        return response


# ── Cache ─────────────────────────────────────────────────────────────────────


class CacheDecorator(RequestHandlerDecorator):
    """Caches GET responses in memory keyed by path + query params.

    Only GET responses are cached; other methods pass through untouched.
    """

    def __init__(self, wrapped: Any, ttl_seconds: int = 30) -> None:
        super().__init__(wrapped)
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[ConcreteHTTPResponse, float]] = {}

    def handle(self, request: ConcreteHTTPRequest) -> ConcreteHTTPResponse:
        if request.method != "GET":
            return self._wrapped.handle(request)

        cache_key = self._make_key(request)
        cached = self._store.get(cache_key)
        if cached:
            response, cached_at = cached
            if time.time() - cached_at < self._ttl:
                response.headers["X-Cache"] = "HIT"
                return response

        response = self._wrapped.handle(request)
        if response.status_code == 200:
            self._store[cache_key] = (response, time.time())
            response.headers["X-Cache"] = "MISS"
        return response

    def _make_key(self, request: ConcreteHTTPRequest) -> str:
        raw = request.path + json.dumps(request.query_params, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def invalidate(self) -> None:
        """Clear all cached entries."""
        self._store.clear()

    @property
    def cached_count(self) -> int:
        return len(self._store)


# ── Compression ───────────────────────────────────────────────────────────────


class CompressionDecorator(RequestHandlerDecorator):
    """Gzip-compresses the response body when the client accepts it."""

    _MIN_COMPRESSIBLE_BYTES = 1024  # only compress responses larger than 1 KB

    def handle(self, request: ConcreteHTTPRequest) -> ConcreteHTTPResponse:
        response = self._wrapped.handle(request)
        accepts_gzip = "gzip" in request.headers.get("Accept-Encoding", "")
        is_large_enough = len(response.body) >= self._MIN_COMPRESSIBLE_BYTES
        if accepts_gzip and is_large_enough:
            response.compress_body()
        return response
