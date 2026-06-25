"""Root URL configuration."""

from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("", include("order_signals.django_app.urls")),
]
