"""URL patterns for the content_export_visitor app."""

from __future__ import annotations

from django.urls import path

from content_export_visitor.django_app.views import export_content, get_export_job

app_name = "content_export_visitor"

urlpatterns = [
    path("exports/jobs/<str:job_id>/", get_export_job, name="job-detail"),
    path("exports/<str:format_name>/", export_content, name="export"),
]
