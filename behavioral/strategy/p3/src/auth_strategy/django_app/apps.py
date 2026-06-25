"""Django AppConfig for the auth_strategy app."""

from __future__ import annotations

from django.apps import AppConfig


class AuthStrategyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_strategy.django_app"
    label = "auth_strategy_django_app"
