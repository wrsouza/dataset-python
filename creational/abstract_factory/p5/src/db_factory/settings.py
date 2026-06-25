"""Django settings for the Database Connector Factory project.

Kept minimal — this is a teaching project focused on the Abstract Factory
pattern, not on production Django configuration.
"""

from __future__ import annotations

import os

# ── Security ───────────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-insecure-key-change-in-prod")
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

# ── Application ────────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "db_factory",
]

ROOT_URLCONF = "db_factory.urls"

MIDDLEWARE: list[str] = [
    "django.middleware.common.CommonMiddleware",
]

# ── Database connections ───────────────────────────────────────────────────────
# Each engine has its own connection alias so Django's routing can
# direct queries and migrations to the correct backend.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "appdb"),
        "USER": os.getenv("POSTGRES_USER", "app"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "secret"),
        "HOST": os.getenv("POSTGRES_HOST", "postgres"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    },
    "mysql": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_DATABASE", "appdb"),
        "USER": os.getenv("MYSQL_USER", "app"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD", "secret"),
        "HOST": os.getenv("MYSQL_HOST", "mysql"),
        "PORT": os.getenv("MYSQL_PORT", "3306"),
    },
    "sqlserver": {
        "ENGINE": "mssql",
        "NAME": os.getenv("SQLSERVER_DATABASE", "appdb"),
        "USER": os.getenv("SQLSERVER_USER", "sa"),
        "PASSWORD": os.getenv("SQLSERVER_PASSWORD", "YourStrong@Passw0rd"),
        "HOST": os.getenv("SQLSERVER_HOST", "sqlserver"),
        "PORT": os.getenv("SQLSERVER_PORT", "1433"),
        "OPTIONS": {
            "driver": "ODBC Driver 18 for SQL Server",
            "extra_params": "TrustServerCertificate=yes",
        },
    },
}

# ── Internationalisation ───────────────────────────────────────────────────────

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True

# ── Misc ───────────────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
