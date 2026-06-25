"""Celery-backed adapter implementing AbstractTaskQueue and AbstractJobStatusReader."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from celery import Celery
from celery.result import AsyncResult

from jobs.domain.entities import JobInfo, JobRequest, JobStatus
from jobs.domain.interfaces import AbstractJobStatusReader, AbstractTaskQueue

_CELERY_TO_DOMAIN_STATUS: dict[str, JobStatus] = {
    "PENDING": JobStatus.PENDING,
    "STARTED": JobStatus.STARTED,
    "SUCCESS": JobStatus.SUCCESS,
    "FAILURE": JobStatus.FAILURE,
    "REVOKED": JobStatus.REVOKED,
    "RETRY": JobStatus.RETRY,
}


class CeleryTaskQueue(AbstractTaskQueue, AbstractJobStatusReader):
    """Adapter that enqueues, cancels, retries and inspects jobs via Celery."""

    def __init__(self, celery_app: Celery) -> None:
        self._app = celery_app

    def enqueue(self, request: JobRequest) -> str:
        """Submit a Celery task asynchronously and return the resulting task id."""
        async_result = self._app.send_task(
            request.task_name,
            args=request.args,
            kwargs=request.kwargs,
            retries=0,
        )
        return str(async_result.id)

    def cancel(self, job_id: str) -> bool:
        """Revoke a Celery task, terminating it if already running."""
        self._app.control.revoke(job_id, terminate=True)
        return True

    def retry(self, job_id: str) -> str:
        """Re-submit the task associated with `job_id` using its original args."""
        previous = AsyncResult(job_id, app=self._app)
        task_name = previous.name or ""
        args = previous.args or ()
        kwargs = previous.kwargs or {}
        new_result = self._app.send_task(task_name, args=args, kwargs=kwargs)
        return str(new_result.id)

    def get_status(self, job_id: str) -> JobInfo:
        """Read the live status of a job directly from the Celery result backend."""
        async_result = AsyncResult(job_id, app=self._app)
        status = _CELERY_TO_DOMAIN_STATUS.get(async_result.status, JobStatus.UNKNOWN)
        error_message = str(async_result.result) if async_result.failed() else None
        result_value: Any = async_result.result if async_result.successful() else None
        return JobInfo(
            job_id=job_id,
            task_name=async_result.name or "",
            status=status,
            created_at=datetime.now(UTC),
            result=result_value,
            error_message=error_message,
            retries=(
                async_result.info.get("retries", 0)
                if isinstance(async_result.info, dict)
                else 0
            ),
        )
