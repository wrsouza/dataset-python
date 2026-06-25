"""Django AppConfig for the jobs app."""

from __future__ import annotations

from django.apps import AppConfig


class JobsAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jobs.django_app"
    label = "jobs_django_app"
