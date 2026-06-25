"""Django ORM repository for export jobs."""

from __future__ import annotations

from content_export_visitor.django_app.models import ExportJobModel
from content_export_visitor.domain.entities import ExportJob
from content_export_visitor.domain.exceptions import ExportJobNotFoundError


class DjangoExportJobRepository:
    def save(self, job: ExportJob) -> None:
        ExportJobModel.objects.create(
            job_id=job.job_id,
            format_name=job.format_name,
            s3_key=job.s3_key,
            created_at=job.created_at,
        )

    def find_by_id(self, job_id: str) -> ExportJob:
        try:
            row = ExportJobModel.objects.get(job_id=job_id)
        except ExportJobModel.DoesNotExist as exc:
            raise ExportJobNotFoundError(job_id) from exc
        return ExportJob(
            job_id=row.job_id,
            format_name=row.format_name,
            s3_key=row.s3_key,
            created_at=row.created_at,
        )
