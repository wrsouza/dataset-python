"""Root HTTP URL configuration."""

from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("", include("realtime_notifications.urls")),
]
