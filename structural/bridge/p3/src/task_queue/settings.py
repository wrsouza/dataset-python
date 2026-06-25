"""Django settings for the Queue Bridge project.

Kept minimal — this is a teaching project focused on the Bridge pattern,
not on production Django configuration. No database-backed models are
used, so DATABASES points at an in-memory sqlite to keep Django happy.
"""

from __future__ import annotations

import os

# ── Security ────────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-insecure-key-change-in-prod")
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

# ── Application ──────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "task_queue",
]

ROOT_URLCONF = "task_queue.urls"

MIDDLEWARE: list[str] = [
    "django.middleware.common.CommonMiddleware",
]

# ── Database ──────────────────────────────────────────────────────────────────
# This project has no persistent models — sqlite in-memory satisfies Django's
# bootstrap requirements without needing a real database service.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# ── Broker connection settings (consumed by infrastructure/brokers.py) ──────

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")

# ── Internationalisation ─────────────────────────────────────────────────────

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True

# ── Misc ──────────────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
