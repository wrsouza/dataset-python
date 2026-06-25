"""Django ORM model used to persist job submission metadata."""

from __future__ import annotations

from django.db import models


class JobRecord(models.Model):
    """Persisted record of a background job submitted through the facade."""

    job_id = models.CharField(max_length=255, unique=True, db_index=True)
    task_name = models.CharField(max_length=255)
    status = models.CharField(max_length=32)
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    retries = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.task_name} ({self.job_id}): {self.status}"
