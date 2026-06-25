"""Django ORM models for the access_control app."""

from __future__ import annotations

from django.db import models

from access_control.domain.entities import Role

_ROLE_CHOICES = [(role.value, role.value) for role in Role]


class UserModel(models.Model):
    """Persistent representation of an application user."""

    objects: models.Manager[UserModel]

    user_id = models.CharField(max_length=64, unique=True, db_index=True)
    username = models.CharField(max_length=64)
    email = models.CharField(max_length=128)
    role = models.CharField(max_length=16, choices=_ROLE_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = "access_control"
        db_table = "access_control_user"

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"


class DocumentModel(models.Model):
    """Persistent representation of a Document resource."""

    objects: models.Manager[DocumentModel]

    doc_id = models.CharField(max_length=64, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    owner_id = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        app_label = "access_control"
        db_table = "access_control_document"

    def __str__(self) -> str:
        return f"{self.doc_id} — {self.title}"


class AuditLogModel(models.Model):
    """Persistent record of every access decision (granted or denied)."""

    objects: models.Manager[AuditLogModel]

    log_id = models.CharField(max_length=64, unique=True, db_index=True)
    user_id = models.CharField(max_length=64, db_index=True)
    action = models.CharField(max_length=16)
    resource_id = models.CharField(max_length=64)
    granted = models.BooleanField()
    reason = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "access_control"
        db_table = "access_control_audit_log"
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        status = "GRANTED" if self.granted else "DENIED"
        return f"[{status}] {self.user_id} {self.action} {self.resource_id}"
