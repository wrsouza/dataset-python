"""JobFacade: a simple interface hiding Celery/Redis enqueueing, status lookup,
cancellation and retry behind a single, cohesive entry point.

This is the Facade pattern: client code (Django views, management commands,
other services) talks only to `JobFacade`. It never imports Celery directly,
never builds an `AsyncResult`, and never touches the persistence layer.
The facade orchestrates three collaborators behind the scenes:

    AbstractTaskQueue        — enqueue / cancel / retry on the broker
    AbstractJobStatusReader  — read live status from the result backend
    AbstractJobRepository    — persist a durable audit trail in the DB
"""

from __future__ import annotations

from datetime import UTC, datetime

from jobs.domain.entities import JobInfo, JobRequest, JobStatus
from jobs.domain.interfaces import (
    AbstractJobRepository,
    AbstractJobStatusReader,
    AbstractTaskQueue,
)


class JobNotFoundError(Exception):
    """Raised when a job id is unknown to both the queue and the repository."""


class JobFacade:
    """Unified, simplified interface for scheduling and monitoring background jobs."""

    def __init__(
        self,
        task_queue: AbstractTaskQueue,
        status_reader: AbstractJobStatusReader,
        repository: AbstractJobRepository,
    ) -> None:
        self._task_queue = task_queue
        self._status_reader = status_reader
        self._repository = repository

    def schedule(self, request: JobRequest) -> JobInfo:
        """Enqueue a new job and persist its initial PENDING record."""
        job_id = self._task_queue.enqueue(request)
        job = JobInfo(
            job_id=job_id,
            task_name=request.task_name,
            status=JobStatus.PENDING,
            created_at=datetime.now(UTC),
        )
        self._repository.save(job)
        return job

    def get_status(self, job_id: str) -> JobInfo:
        """Return the latest known status of a job, refreshing the audit trail."""
        job = self._status_reader.get_status(job_id)
        if job.status is JobStatus.UNKNOWN:
            persisted = self._repository.find_by_id(job_id)
            if persisted is None:
                raise JobNotFoundError(f"Job {job_id} was not found.")
            return persisted
        self._repository.save(job)
        return job

    def cancel(self, job_id: str) -> bool:
        """Cancel a pending or running job and mark it REVOKED in the repository."""
        cancelled = self._task_queue.cancel(job_id)
        if cancelled:
            existing = self._repository.find_by_id(job_id)
            task_name = existing.task_name if existing else ""
            self._repository.save(
                JobInfo(
                    job_id=job_id,
                    task_name=task_name,
                    status=JobStatus.REVOKED,
                    created_at=datetime.now(UTC),
                )
            )
        return cancelled

    def retry(self, job_id: str) -> JobInfo:
        """Resubmit a failed job, returning a new JobInfo for the retried job."""
        new_job_id = self._task_queue.retry(job_id)
        previous = self._repository.find_by_id(job_id)
        task_name = previous.task_name if previous else ""
        retries = (previous.retries + 1) if previous else 1
        job = JobInfo(
            job_id=new_job_id,
            task_name=task_name,
            status=JobStatus.RETRY,
            created_at=datetime.now(UTC),
            retries=retries,
        )
        self._repository.save(job)
        return job
