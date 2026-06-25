"""Django ORM model used to persist command execution records."""

from __future__ import annotations

from django.db import models


class ExecutionRecordModel(models.Model):
    """Persisted outcome of dispatching one ScheduledCommand to a worker."""

    objects: models.Manager[ExecutionRecordModel]

    job_id = models.CharField(max_length=64, unique=True, db_index=True)
    command_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    result_message = models.TextField()
    executed_at = models.DateTimeField()

    class Meta:
        ordering = ["-executed_at"]

    def __str__(self) -> str:
        return f"{self.job_id} ({self.status})"
