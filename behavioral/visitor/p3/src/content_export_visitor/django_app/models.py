"""Django ORM model logging each export job, after its content is uploaded
to S3."""

from __future__ import annotations

from django.db import models


class ExportJobModel(models.Model):
    objects: models.Manager[ExportJobModel]

    job_id = models.CharField(max_length=64, unique=True, db_index=True)
    format_name = models.CharField(max_length=20)
    s3_key = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.job_id} ({self.format_name})"
