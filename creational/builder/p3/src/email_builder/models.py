"""Django model for email send logs."""

from __future__ import annotations

from django.db import models

from email_builder.domain.entities import TemplateType


class EmailLog(models.Model):
    """Persists every email send attempt — success or failure."""

    template_type = models.CharField(
        max_length=50,
        choices=[(t.value, t.value) for t in TemplateType],
    )
    recipient = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("sent", "Sent"), ("failed", "Failed")],
        default="sent",
    )
    message_id = models.CharField(max_length=255, blank=True, default="")
    error_message = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self) -> str:
        return f"{self.template_type} → {self.recipient} [{self.status}]"
