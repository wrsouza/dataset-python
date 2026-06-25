"""HTTP views exposing the scheduled command executor: trigger and status."""

from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from scheduled_executor.application.use_cases import (
    ExecutionNotFoundError,
    GetExecutionUseCase,
    TriggerCommandUseCase,
)
from scheduled_executor.domain.entities import ExecutionRecord
from scheduled_executor.infrastructure.celery_app import run_command_task
from scheduled_executor.infrastructure.commands import UnknownCommandError
from scheduled_executor.infrastructure.repository import DjangoExecutionRepository


def _record_to_dict(record: ExecutionRecord) -> dict[str, object]:
    return {
        "job_id": record.job_id,
        "command_name": record.command_name,
        "status": record.status.value,
        "result_message": record.result_message,
        "executed_at": record.executed_at.isoformat(),
    }


def _get_trigger_use_case() -> TriggerCommandUseCase:
    return TriggerCommandUseCase(run_command_task, DjangoExecutionRepository())


def _get_status_use_case() -> GetExecutionUseCase:
    return GetExecutionUseCase(DjangoExecutionRepository())


@csrf_exempt
@require_http_methods(["POST"])
def trigger_command(request: HttpRequest) -> JsonResponse:
    """POST /commands/trigger/ — dispatch a command to a Celery worker."""
    payload = json.loads(request.body or "{}")
    command_name = payload.get("command_name", "")
    try:
        record = _get_trigger_use_case().execute(
            command_name, payload.get("payload", {})
        )
    except UnknownCommandError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse(_record_to_dict(record), status=201)


@require_http_methods(["GET"])
def execution_status(request: HttpRequest, job_id: str) -> JsonResponse:
    """GET /commands/<job_id>/ — return the recorded outcome of a dispatch."""
    try:
        record = _get_status_use_case().execute(job_id)
    except ExecutionNotFoundError as exc:
        return JsonResponse({"error": str(exc)}, status=404)
    return JsonResponse(_record_to_dict(record))
