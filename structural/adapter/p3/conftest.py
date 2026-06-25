"""pytest configuration for cloud_adapter tests."""

from __future__ import annotations

import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cloud_adapter.settings")
django.setup()
