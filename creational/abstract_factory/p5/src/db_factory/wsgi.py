"""WSGI config for the Database Connector Factory Django project."""

from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "db_factory.settings")

application = get_wsgi_application()
