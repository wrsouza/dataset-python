"""Root URL configuration."""

from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("", include("etl_pipeline_template.django_app.urls")),
]
