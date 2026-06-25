"""Django AppConfig for the order_signals app."""

from __future__ import annotations

from django.apps import AppConfig


class OrderSignalsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "order_signals.django_app"
    label = "order_signals_django_app"
