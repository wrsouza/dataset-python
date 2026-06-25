"""Django AppConfig for the scheduled_executor app."""

from __future__ import annotations

from django.apps import AppConfig


class ScheduledExecutorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "scheduled_executor.django_app"
    label = "scheduled_executor_django_app"
