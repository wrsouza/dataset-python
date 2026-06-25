"""Django ORM models — the only place the project touches PostgreSQL directly.

Kept at the conventional `<app>/models.py` location so Django's app
registry and the mypy django-stubs plugin can resolve them without extra
configuration. The domain layer never imports this module;
`DjangoResourceRepository` (see infrastructure/repository.py) is the single
translation point between Django model instances and the
framework-agnostic `Resource` entity.
"""

from __future__ import annotations

from django.db import models


class DocumentModel(models.Model):
    """Persisted representation of a protected document resource."""

    objects: models.Manager[DocumentModel]

    resource_id = models.CharField(max_length=64, unique=True)
    owner_id = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "permission_layers_document"

    def __str__(self) -> str:
        return f"DocumentModel({self.resource_id})"


class AccessLogModel(models.Model):
    """Persisted audit trail — one row per access attempt evaluated."""

    objects: models.Manager[AccessLogModel]

    resource_id = models.CharField(max_length=64)
    user_id = models.CharField(max_length=64)
    action = models.CharField(max_length=16)
    granted = models.BooleanField()
    reason = models.CharField(max_length=255)
    layers_applied = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "permission_layers_access_log"

    def __str__(self) -> str:
        outcome = "GRANTED" if self.granted else "DENIED"
        return f"AccessLogModel({self.resource_id}, {outcome})"
