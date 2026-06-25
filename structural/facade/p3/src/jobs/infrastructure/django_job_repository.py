"""Django ORM adapter implementing AbstractJobRepository."""

from __future__ import annotations

from jobs.django_app.models import JobRecord
from jobs.domain.entities import JobInfo, JobStatus
from jobs.domain.interfaces import AbstractJobRepository


class DjangoJobRepository(AbstractJobRepository):
    """Persists job metadata using the Django ORM (JobRecord model)."""

    def save(self, job: JobInfo) -> None:
        """Create or update the JobRecord row matching `job.job_id`."""
        JobRecord.objects.update_or_create(
            job_id=job.job_id,
            defaults={
                "task_name": job.task_name,
                "status": job.status.value,
                "result": job.result,
                "error_message": job.error_message,
                "retries": job.retries,
            },
        )

    def find_by_id(self, job_id: str) -> JobInfo | None:
        """Return the JobInfo for `job_id`, or None if never persisted."""
        try:
            record = JobRecord.objects.get(job_id=job_id)
        except JobRecord.DoesNotExist:
            return None
        return JobInfo(
            job_id=record.job_id,
            task_name=record.task_name,
            status=JobStatus(record.status),
            created_at=record.created_at,
            result=record.result,
            error_message=record.error_message,
            retries=record.retries,
        )
