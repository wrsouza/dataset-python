"""Django ORM models for workflow requests and their notification log."""

from __future__ import annotations

from django.db import models


class WorkflowRequestModel(models.Model):
    """Current state of an approval workflow request."""

    objects: models.Manager[WorkflowRequestModel]

    request_id = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    state = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"{self.request_id} ({self.state})"


class NotificationLogModel(models.Model):
    """Written by the Celery task dispatched on every state transition."""

    objects: models.Manager[NotificationLogModel]

    request_id = models.CharField(max_length=64, db_index=True)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    class Meta:
        ordering = ["created_at"]
