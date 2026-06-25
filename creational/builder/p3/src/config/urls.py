"""Root URL configuration."""

from __future__ import annotations

from django.http import JsonResponse
from django.urls import include, path


def health_check(request):  # type: ignore[no-untyped-def]
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", include("email_builder.urls")),
    path("health", health_check, name="health"),
]
