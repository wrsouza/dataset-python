"""URL patterns for the auth_strategy app."""

from __future__ import annotations

from django.urls import path

from auth_strategy.django_app.views import auth_attempts, authenticate

app_name = "auth_strategy"

urlpatterns = [
    path("auth/attempts/", auth_attempts, name="attempts"),
    path("auth/<str:strategy_name>/", authenticate, name="authenticate"),
]
