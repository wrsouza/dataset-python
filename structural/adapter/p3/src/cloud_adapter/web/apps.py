"""Django AppConfig for cloud_adapter."""

from __future__ import annotations

from django.apps import AppConfig


class CloudAdapterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cloud_adapter.web"
    label = "cloud_adapter"
    verbose_name = "Cloud Adapter"
