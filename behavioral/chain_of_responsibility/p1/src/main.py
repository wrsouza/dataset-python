"""FastAPI composition root for the request validation chain demo."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.datastructures import Headers

from validation.application.validate_request_use_case import (
    ValidateRequestUseCase,
    build_default_chain,
)
from validation.domain.entities import APIRequest, UserRole
from validation.infrastructure.handlers.jwt_auth import JWTAuthHandler
from validation.infrastructure.handlers.rate_limit import RateLimitHandler
from validation.infrastructure.handlers.role_authorization import (
    RoleAuthorizationHandler,
)
from validation.infrastructure.handlers.schema_validation import (
    SchemaValidationHandler,
)

app = FastAPI(
    title="Chain of Responsibility — Request Validation Chain",
    description=(
        "Demonstrates the Chain of Responsibility pattern validating "
        "incoming HTTP requests through a pipeline of independent handlers."
    ),
    version="0.1.0",
)

# Composition root: the only place that wires concrete handlers together.
# Reordering, adding, or removing a handler here never requires touching
# the handlers themselves (Open/Closed Principle).
_chain_entry_point = build_default_chain(
    RateLimitHandler(),
    JWTAuthHandler(),
    RoleAuthorizationHandler(),
    SchemaValidationHandler(),
)
_use_case = ValidateRequestUseCase(entry_handler=_chain_entry_point)


def _normalize_authorization_header(headers: Headers) -> dict[str, str]:
    """Re-key incoming headers so 'Authorization' matches handler lookups.

    Starlette's ``Headers`` are case-insensitive, but ``APIRequest.headers``
    is a plain dict — the handlers (e.g. ``JWTAuthHandler``) look up the
    exact key 'Authorization'. This keeps that pre-existing handler
    convention untouched while bridging the HTTP layer correctly.
    """
    normalized = dict(headers)
    if "authorization" in normalized:
        normalized["Authorization"] = normalized.pop("authorization")
    return normalized


@app.get("/health")
def health_check() -> dict[str, str]:
    """Liveness probe used by docker-compose and orchestrators."""
    return {"status": "ok"}


@app.post("/orders")
async def create_order(request: Request) -> JSONResponse:
    """Submit an order request through the validation chain.

    The handler chain (rate limit -> JWT auth -> role authorization ->
    schema validation) decides whether the request reaches this point as
    successful or is short-circuited earlier with an error response.
    """
    body = await request.json()
    api_request = APIRequest(
        body=body,
        headers=_normalize_authorization_header(request.headers),
        client_ip=request.client.host if request.client else "127.0.0.1",
        endpoint="/orders",
    )

    response = _use_case.execute(api_request)
    return JSONResponse(
        status_code=response.status_code,
        content={
            "message": response.message,
            "data": response.data,
            "handler": response.handler_name,
        },
    )


__all__ = ["app", "UserRole"]
