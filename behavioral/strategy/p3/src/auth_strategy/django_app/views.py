"""HTTP views exposing the Authentication Strategy system."""

from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from auth_strategy.application.use_cases import (
    AuthenticateInput,
    AuthenticateUseCase,
    GetAuthAttemptsUseCase,
)
from auth_strategy.domain.entities import AuthResult
from auth_strategy.domain.exceptions import InvalidStrategyError
from auth_strategy.infrastructure.repository import DjangoAuthAttemptLogRepository


def _result_to_dict(result: AuthResult) -> dict[str, object]:
    return {
        "success": result.success,
        "strategy_name": result.strategy_name,
        "user_id": result.user_id,
        "reason": result.reason,
    }


@csrf_exempt
@require_http_methods(["POST"])
def authenticate(request: HttpRequest, strategy_name: str) -> JsonResponse:
    """POST /auth/<strategy_name>/ — authenticate with the given strategy."""
    credentials = json.loads(request.body or "{}")
    use_case = AuthenticateUseCase(DjangoAuthAttemptLogRepository())
    try:
        result = use_case.execute(
            AuthenticateInput(strategy_name=strategy_name, credentials=credentials)
        )
    except InvalidStrategyError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    status = 200 if result.success else 401
    return JsonResponse(_result_to_dict(result), status=status)


@require_http_methods(["GET"])
def auth_attempts(request: HttpRequest) -> JsonResponse:
    """GET /auth/attempts/ — list every authentication attempt logged."""
    use_case = GetAuthAttemptsUseCase(DjangoAuthAttemptLogRepository())
    history = use_case.execute()
    return JsonResponse([_result_to_dict(r) for r in history], safe=False)
