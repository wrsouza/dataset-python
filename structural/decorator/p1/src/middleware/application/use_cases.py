"""Application layer — assembles the decorator chain at runtime.

This is the composition root for the middleware pipeline.
Demonstrates that the order of decorators is flexible and composable.
"""

from __future__ import annotations

from middleware.domain.entities import ConcreteHTTPRequest, ConcreteHTTPResponse
from middleware.domain.interfaces import RequestHandler
from middleware.infrastructure.decorators import (
    AuthDecorator,
    CacheDecorator,
    CompressionDecorator,
    LoggingDecorator,
    RateLimitDecorator,
)


class BaseRequestHandler(RequestHandler):
    """ConcreteComponent — the real business logic without any cross-cutting concerns."""

    def handle(self, request: ConcreteHTTPRequest) -> ConcreteHTTPResponse:
        body = f'{{"path": "{request.path}", "method": "{request.method}"}}'.encode()
        return ConcreteHTTPResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body=body,
        )


def build_full_pipeline(
    max_requests_per_minute: int = 60,
    cache_ttl_seconds: int = 30,
) -> RequestHandler:
    """Build the default middleware chain.

    Chain (outer → inner):
        CompressionDecorator
            └── LoggingDecorator
                    └── CacheDecorator
                            └── RateLimitDecorator
                                    └── AuthDecorator
                                            └── BaseRequestHandler
    """
    handler: RequestHandler = BaseRequestHandler()
    handler = AuthDecorator(handler)
    handler = RateLimitDecorator(handler, max_requests_per_minute)
    handler = CacheDecorator(handler, cache_ttl_seconds)
    handler = LoggingDecorator(handler)
    handler = CompressionDecorator(handler)
    return handler


def build_public_pipeline() -> RequestHandler:
    """Build a pipeline without authentication (for public endpoints).

    Demonstrates runtime composability: omit AuthDecorator with no code change.
    """
    handler: RequestHandler = BaseRequestHandler()
    handler = RateLimitDecorator(handler, max_requests_per_minute=120)
    handler = LoggingDecorator(handler)
    handler = CompressionDecorator(handler)
    return handler


def build_minimal_pipeline() -> RequestHandler:
    """Minimal pipeline: only logging around the base handler."""
    return LoggingDecorator(BaseRequestHandler())
