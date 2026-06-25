"""URL configuration for the permission_layers Django project."""

from __future__ import annotations

from django.urls import path

from permission_layers.views.api import evaluate_access

urlpatterns = [
    path("access/evaluate", evaluate_access, name="evaluate_access"),
]
