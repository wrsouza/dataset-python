"""Django AppConfig for the etl_pipeline_template app."""

from __future__ import annotations

from django.apps import AppConfig


class EtlPipelineTemplateConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "etl_pipeline_template.django_app"
    label = "etl_pipeline_template_django_app"
