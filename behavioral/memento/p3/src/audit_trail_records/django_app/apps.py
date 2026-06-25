"""Django AppConfig for the audit_trail_records app."""

from __future__ import annotations

from django.apps import AppConfig


class AuditTrailRecordsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "audit_trail_records.django_app"
    label = "audit_trail_records_django_app"
