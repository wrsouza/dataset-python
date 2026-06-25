"""Django ORM model for moderated content submissions."""

from __future__ import annotations

from django.db import models


class SubmissionModel(models.Model):
    """Persistent representation of a ContentSubmission."""

    objects: models.Manager[SubmissionModel]

    submission_id = models.CharField(max_length=64, unique=True, db_index=True)
    author = models.CharField(max_length=150)
    text = models.TextField()
    status = models.CharField(max_length=20)
    history = models.JSONField(default=list)

    class Meta:
        app_label = "moderation"
        db_table = "moderation_submission"

    def __str__(self) -> str:
        return f"{self.submission_id} ({self.status})"
