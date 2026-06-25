"""Django views — thin HTTP adapters delegating to the use case.

Views never build decorator stacks themselves; they only translate
HTTP requests into `EvaluateAccessRequest` objects and the use case's
`ResourceAccessResult` back into JSON (Single Responsibility).
"""

from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from permission_layers.application.use_cases import (
    EvaluateAccessRequest,
    EvaluateDocumentAccessUseCase,
)
from permission_layers.domain.entities import AccessAction, User
from permission_layers.infrastructure.repository import DjangoResourceRepository
from permission_layers.models import AccessLogModel


def _persist_audit_row(result: object, action: str) -> None:
    """Write one audit row per evaluated access attempt — best-effort.

    Kept outside the domain decorators on purpose: persisting to PostgreSQL
    is an infrastructure concern, not a business rule (Single Responsibility,
    Dependency Inversion — the AuditLogDecorator only logs, it does not know
    about the database).
    """
    from permission_layers.domain.entities import ResourceAccessResult

    assert isinstance(result, ResourceAccessResult)
    AccessLogModel.objects.create(
        resource_id=result.resource_id,
        user_id=result.user_id,
        action=action,
        granted=result.granted,
        reason=result.reason,
        layers_applied=",".join(result.layers_applied),
    )


@csrf_exempt
@require_POST
def evaluate_access(request: HttpRequest) -> JsonResponse:
    """POST /access/evaluate — run the permission decorator stack for a request.

    Body: {
      "user_id": str, "username": str, "roles": [str], "is_authenticated": bool,
      "resource_id": str, "owner_id": str, "title": str,
      "action": "read" | "write" | "delete", "required_role": str | null
    }
    """
    payload = json.loads(request.body or b"{}")
    user = User(
        user_id=payload.get("user_id", ""),
        username=payload.get("username", "anonymous"),
        roles=frozenset(payload.get("roles", [])),
        is_authenticated=payload.get("is_authenticated", False),
    )
    use_case = EvaluateDocumentAccessUseCase(DjangoResourceRepository())
    result = use_case.execute(
        EvaluateAccessRequest(
            user=user,
            resource_id=payload["resource_id"],
            owner_id=payload.get("owner_id", ""),
            title=payload.get("title", ""),
            action=AccessAction(payload.get("action", "read")),
            required_role=payload.get("required_role"),
        )
    )
    _persist_audit_row(result, payload.get("action", "read"))
    return JsonResponse(
        {
            "granted": result.granted,
            "reason": result.reason,
            "resource_id": result.resource_id,
            "user_id": result.user_id,
            "layers_applied": list(result.layers_applied),
        },
        status=200 if result.granted else 403,
    )
