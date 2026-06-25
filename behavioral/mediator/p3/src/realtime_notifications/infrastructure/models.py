"""Django ORM model for persisted notifications."""

from __future__ import annotations

from django.db import models


class NotificationModel(models.Model):
    """Persistent representation of a Notification."""

    objects: models.Manager[NotificationModel]

    group = models.CharField(max_length=100, db_index=True)
    message = models.JSONField()
    created_at = models.DateTimeField()

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.group} @ {self.created_at.isoformat()}"
