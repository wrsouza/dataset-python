"""Root URL configuration for cloud_adapter Django project."""

from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("", include("cloud_adapter.web.urls")),
]
