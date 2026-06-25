"""URL patterns for the moderation app."""

from __future__ import annotations

from django.urls import path

from moderation.views import SubmissionDetailView, SubmitContentView

app_name = "moderation"

urlpatterns = [
    path("submissions/", SubmitContentView.as_view(), name="submission-create"),
    path(
        "submissions/<str:submission_id>/",
        SubmissionDetailView.as_view(),
        name="submission-detail",
    ),
]
