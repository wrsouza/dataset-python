"""URL routes for the jobs app."""

from __future__ import annotations

from django.urls import path

from jobs.django_app import views

urlpatterns = [
    path("jobs/", views.schedule_job, name="schedule_job"),
    path("jobs/<str:job_id>/", views.job_status, name="job_status"),
    path("jobs/<str:job_id>/cancel/", views.cancel_job, name="cancel_job"),
    path("jobs/<str:job_id>/retry/", views.retry_job, name="retry_job"),
]
