"""WSGI entry point — initialises the FeatureFlagManager singleton at startup."""

from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Eagerly import and configure the singleton before the first request.
# This ensures the cold-start cost (JSON load) is paid during server startup,
# not on the first user request.
from feature_flags.infrastructure.loaders import JsonFlagLoader
from feature_flags.infrastructure.singleton import FeatureFlagManager

_flags_path = os.getenv("FLAGS_JSON_PATH", "/app/src/flags.json")
FeatureFlagManager(loader=JsonFlagLoader(_flags_path))

application = get_wsgi_application()
