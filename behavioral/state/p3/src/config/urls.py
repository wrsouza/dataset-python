"""Root URL configuration."""

from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("", include("workflow_approval_fsm.django_app.urls")),
]
