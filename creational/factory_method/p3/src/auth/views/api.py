"""Django views for the Auth Provider Factory API.

SRP: each view handles exactly one HTTP endpoint and delegates business
logic to the application use cases — views never instantiate a concrete
AuthProvider directly (DIP).
"""

from __future__ import annotations

import json
from typing import Any

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from auth.application.use_cases import LoginUseCase, LogoutUseCase, ValidateTokenUseCase
from auth.domain.entities import (
    AuthenticationError,
    InvalidTokenError,
    UnsupportedSchemeError,
)
from auth.infrastructure.creators import get_factory


def _parse_body(request: HttpRequest) -> dict[str, Any]:
    try:
        body: dict[str, Any] = json.loads(request.body or b"{}")
        return body
    except json.JSONDecodeError:
        return {}


@csrf_exempt
@require_POST
def login(request: HttpRequest, scheme: str) -> JsonResponse:
    """POST /auth/<scheme>/login — authenticate and issue a token."""
    body = _parse_body(request)
    try:
        factory = get_factory(scheme)
        result = LoginUseCase(factory).execute(body)
    except UnsupportedSchemeError as exc:
        return JsonResponse({"error": str(exc)}, status=404)
    except AuthenticationError as exc:
        return JsonResponse({"error": str(exc)}, status=401)
    return JsonResponse(
        {"user_id": result.user_id, "scheme": result.scheme, "token": result.token}
    )


@csrf_exempt
@require_POST
def validate(request: HttpRequest, scheme: str) -> JsonResponse:
    """POST /auth/<scheme>/validate — validate a token, return the user id."""
    body = _parse_body(request)
    token = body.get("token", "")
    try:
        factory = get_factory(scheme)
        user_id = ValidateTokenUseCase(factory).execute(token)
    except UnsupportedSchemeError as exc:
        return JsonResponse({"error": str(exc)}, status=404)
    except InvalidTokenError as exc:
        return JsonResponse({"error": str(exc)}, status=401)
    return JsonResponse({"user_id": user_id, "scheme": scheme})


@csrf_exempt
@require_POST
def logout(request: HttpRequest, scheme: str) -> JsonResponse:
    """POST /auth/<scheme>/logout — revoke a token."""
    body = _parse_body(request)
    token = body.get("token", "")
    try:
        factory = get_factory(scheme)
        LogoutUseCase(factory).execute(token)
    except UnsupportedSchemeError as exc:
        return JsonResponse({"error": str(exc)}, status=404)
    return JsonResponse({"message": "logged out", "scheme": scheme})
