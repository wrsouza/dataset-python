"""WSGI config for cloud_adapter Django project."""

from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cloud_adapter.settings")

application = get_wsgi_application()
