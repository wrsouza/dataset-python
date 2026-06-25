"""HTTP views exposing the Workflow Approval FSM."""

from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from workflow_approval_fsm.application.use_cases import (
    ApproveWorkflowRequestUseCase,
    CreateWorkflowRequestInput,
    CreateWorkflowRequestUseCase,
    GetWorkflowRequestUseCase,
    RejectWorkflowRequestUseCase,
    RequestChangesUseCase,
    SubmitWorkflowRequestUseCase,
    TransitionUseCase,
    WorkflowRequestNotFoundError,
)
from workflow_approval_fsm.domain.entities import WorkflowRequest
from workflow_approval_fsm.domain.interfaces import InvalidTransitionError
from workflow_approval_fsm.infrastructure.repository import DjangoWorkflowRepository


def _request_to_dict(request: WorkflowRequest) -> dict[str, object]:
    return {
        "request_id": request.request_id,
        "title": request.title,
        "state": request.get_current_state_name(),
        "allowed_transitions": request.get_allowed_transitions(),
    }


@csrf_exempt
@require_http_methods(["POST"])
def create_request(request: HttpRequest) -> JsonResponse:
    """POST /workflows/ — create a workflow request in Draft."""
    payload = json.loads(request.body or "{}")
    use_case = CreateWorkflowRequestUseCase(DjangoWorkflowRepository())
    workflow_request = use_case.execute(
        CreateWorkflowRequestInput(
            request_id=payload["request_id"], title=payload["title"]
        )
    )
    return JsonResponse(_request_to_dict(workflow_request), status=201)


def _run_transition(
    use_case_cls: type[TransitionUseCase], request_id: str
) -> JsonResponse:
    use_case = use_case_cls(DjangoWorkflowRepository())
    try:
        workflow_request = use_case.execute(request_id)
    except WorkflowRequestNotFoundError as exc:
        return JsonResponse({"error": str(exc)}, status=404)
    except InvalidTransitionError as exc:
        return JsonResponse({"error": str(exc)}, status=409)
    return JsonResponse(_request_to_dict(workflow_request))


@csrf_exempt
@require_http_methods(["POST"])
def submit_request(request: HttpRequest, request_id: str) -> JsonResponse:
    """POST /workflows/<request_id>/submit/"""
    return _run_transition(SubmitWorkflowRequestUseCase, request_id)


@csrf_exempt
@require_http_methods(["POST"])
def approve_request(request: HttpRequest, request_id: str) -> JsonResponse:
    """POST /workflows/<request_id>/approve/"""
    return _run_transition(ApproveWorkflowRequestUseCase, request_id)


@csrf_exempt
@require_http_methods(["POST"])
def reject_request(request: HttpRequest, request_id: str) -> JsonResponse:
    """POST /workflows/<request_id>/reject/"""
    return _run_transition(RejectWorkflowRequestUseCase, request_id)


@csrf_exempt
@require_http_methods(["POST"])
def request_changes(request: HttpRequest, request_id: str) -> JsonResponse:
    """POST /workflows/<request_id>/request-changes/"""
    return _run_transition(RequestChangesUseCase, request_id)


@require_http_methods(["GET"])
def get_request(request: HttpRequest, request_id: str) -> JsonResponse:
    """GET /workflows/<request_id>/"""
    use_case = GetWorkflowRequestUseCase(DjangoWorkflowRepository())
    workflow_request = use_case.execute(request_id)
    if workflow_request is None:
        return JsonResponse(
            {"error": f"Workflow request '{request_id}' not found"}, status=404
        )
    return JsonResponse(_request_to_dict(workflow_request))
