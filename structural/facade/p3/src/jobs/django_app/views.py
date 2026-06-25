"""HTTP views exposing the JobFacade: schedule, status, cancel, retry."""

from __future__ import annotations

import json
from typing import Any

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from jobs.application.facade import JobFacade, JobNotFoundError
from jobs.domain.entities import JobInfo, JobRequest
from jobs.infrastructure.factory import build_job_facade

_AVAILABLE_TASKS = {"jobs.send_report", "jobs.process_dataset"}


def _job_info_to_dict(job: JobInfo) -> dict[str, Any]:
    return {
        "job_id": job.job_id,
        "task_name": job.task_name,
        "status": job.status.value,
        "created_at": job.created_at.isoformat(),
        "result": job.result,
        "error_message": job.error_message,
        "retries": job.retries,
    }


def _get_facade() -> JobFacade:
    return build_job_facade()


@csrf_exempt
@require_http_methods(["POST"])
def schedule_job(request: HttpRequest) -> JsonResponse:
    """POST /jobs/ — enqueue a new background job."""
    payload = json.loads(request.body or "{}")
    task_name = payload.get("task_name")
    if task_name not in _AVAILABLE_TASKS:
        return JsonResponse(
            {"error": f"Unknown task_name. Use one of {sorted(_AVAILABLE_TASKS)}."},
            status=400,
        )
    job_request = JobRequest(
        task_name=task_name,
        args=tuple(payload.get("args", [])),
        kwargs=payload.get("kwargs", {}),
    )
    job = _get_facade().schedule(job_request)
    return JsonResponse(_job_info_to_dict(job), status=201)


@require_http_methods(["GET"])
def job_status(request: HttpRequest, job_id: str) -> JsonResponse:
    """GET /jobs/{job_id}/ — return the current status of a job."""
    try:
        job = _get_facade().get_status(job_id)
    except JobNotFoundError:
        return JsonResponse({"error": "Job not found."}, status=404)
    return JsonResponse(_job_info_to_dict(job))


@csrf_exempt
@require_http_methods(["POST"])
def cancel_job(request: HttpRequest, job_id: str) -> JsonResponse:
    """POST /jobs/{job_id}/cancel/ — cancel a pending or running job."""
    cancelled = _get_facade().cancel(job_id)
    return JsonResponse({"job_id": job_id, "cancelled": cancelled})


@csrf_exempt
@require_http_methods(["POST"])
def retry_job(request: HttpRequest, job_id: str) -> JsonResponse:
    """POST /jobs/{job_id}/retry/ — resubmit a failed job."""
    job = _get_facade().retry(job_id)
    return JsonResponse(_job_info_to_dict(job), status=201)
