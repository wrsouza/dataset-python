"""URL patterns for the access_control app."""

from __future__ import annotations

from django.urls import path

from access_control.views import DocumentDetailView, DocumentListCreateView

app_name = "access_control"

urlpatterns = [
    path("documents/", DocumentListCreateView.as_view(), name="document-list"),
    path(
        "documents/<str:doc_id>/",
        DocumentDetailView.as_view(),
        name="document-detail",
    ),
]
