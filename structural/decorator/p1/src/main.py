"""FastAPI application — exposes the decorator pipeline through HTTP endpoints.

Shows how the same handler chain can be reused for different endpoints,
and how decorators can be added/removed per-endpoint.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response

from middleware.application.use_cases import (
    build_full_pipeline,
    build_minimal_pipeline,
    build_public_pipeline,
)
from middleware.domain.entities import (
    AuthenticationError,
    ConcreteHTTPRequest,
    RateLimitExceededError,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

app = FastAPI(
    title="HTTP Middleware Pipeline — Decorator Pattern",
    description=(
        "Demonstrates the GoF Decorator pattern applied to HTTP middleware. "
        "Each middleware layer (Auth, RateLimit, Logging, Cache, Compression) "
        "is an independent decorator class."
    ),
    version="1.0.0",
)

_full_pipeline = build_full_pipeline(max_requests_per_minute=60, cache_ttl_seconds=30)
_public_pipeline = build_public_pipeline()
_minimal_pipeline = build_minimal_pipeline()


def _adapt_request(fastapi_request: Request, body: bytes = b"") -> ConcreteHTTPRequest:
    """Adapt a FastAPI Request into our domain entity."""
    return ConcreteHTTPRequest(
        method=fastapi_request.method,
        path=str(fastapi_request.url.path),
        headers=dict(fastapi_request.headers),
        body=body,
        query_params=dict(fastapi_request.query_params),
        client_ip=fastapi_request.client.host if fastapi_request.client else "unknown",
    )


def _adapt_response(domain_response: "ConcreteHTTPResponse") -> Response:  # type: ignore[name-defined]
    """Adapt our domain response entity to a FastAPI Response."""
    return Response(
        content=domain_response.body,
        status_code=domain_response.status_code,
        headers=domain_response.headers,
    )


@app.exception_handler(AuthenticationError)
async def auth_error_handler(_: Request, exc: AuthenticationError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"error": exc.reason})


@app.exception_handler(RateLimitExceededError)
async def rate_limit_handler(_: Request, exc: RateLimitExceededError) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"error": f"Rate limit exceeded: {exc.limit}/min"},
        headers={"Retry-After": "60"},
    )


@app.get("/", tags=["info"])
async def root() -> dict[str, str]:
    """Service health check — no middleware applied."""
    return {"service": "HTTP Middleware Pipeline", "pattern": "Decorator (GoF)"}


@app.api_route(
    "/api/protected/{path:path}",
    methods=["GET", "POST"],
    tags=["protected"],
    summary="Full pipeline: Auth + RateLimit + Cache + Logging + Compression",
)
async def protected_endpoint(path: str, request: Request) -> Response:
    """Uses the full decorator chain including JWT authentication."""
    domain_req = _adapt_request(request)
    domain_req.path = f"/{path}"
    domain_resp = _full_pipeline.handle(domain_req)
    return _adapt_response(domain_resp)


@app.api_route(
    "/api/public/{path:path}",
    methods=["GET"],
    tags=["public"],
    summary="Public pipeline: RateLimit + Logging + Compression (no auth)",
)
async def public_endpoint(path: str, request: Request) -> Response:
    """Public endpoint — Auth decorator is intentionally absent."""
    domain_req = _adapt_request(request)
    domain_req.path = f"/{path}"
    domain_resp = _public_pipeline.handle(domain_req)
    return _adapt_response(domain_resp)


@app.get(
    "/api/minimal",
    tags=["debug"],
    summary="Minimal pipeline: only Logging around base handler",
)
async def minimal_endpoint(request: Request) -> Response:
    """Demonstrates that decorators can be composed selectively."""
    domain_req = _adapt_request(request)
    domain_resp = _minimal_pipeline.handle(domain_req)
    return _adapt_response(domain_resp)


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
