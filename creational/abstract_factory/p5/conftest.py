"""pytest configuration for db_factory tests."""

from __future__ import annotations

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "db_factory.settings")
django.setup()
