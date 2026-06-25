"""Django AppConfig for the catalog_iterator app."""

from __future__ import annotations

from django.apps import AppConfig


class CatalogIteratorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog_iterator"
    label = "catalog_iterator"
