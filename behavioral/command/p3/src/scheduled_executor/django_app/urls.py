"""URL patterns for the scheduled_executor app."""

from __future__ import annotations

from django.urls import path

from scheduled_executor.django_app.views import execution_status, trigger_command

app_name = "scheduled_executor"

urlpatterns = [
    path("commands/trigger/", trigger_command, name="trigger"),
    path("commands/<str:job_id>/", execution_status, name="status"),
]
