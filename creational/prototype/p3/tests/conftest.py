"""Pytest configuration: use SQLite for tests instead of MySQL."""
from __future__ import annotations

import django
from django.conf import settings


def pytest_configure() -> None:
    """Override database to SQLite for fast, containerless tests."""
    if not settings.configured:
        settings.configure(
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "products.apps.ProductsConfig",
            ],
            ROOT_URLCONF="config.urls",
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
            USE_TZ=True,
        )
    django.setup()
