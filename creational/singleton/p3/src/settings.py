"""Django settings for the feature_flags project."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-insecure-key-change-in-prod")

DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"

ALLOWED_HOSTS: list[str] = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS: list[str] = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
]

MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "feature_flags.middleware.feature_flag_middleware.FeatureFlagMiddleware",
]

ROOT_URLCONF = "urls"

DATABASES: dict = {}

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Feature Flags config ─────────────────────────────────────────────────────

FLAGS_JSON_PATH = os.getenv(
    "FLAGS_JSON_PATH",
    str(BASE_DIR / "flags.json"),
)
