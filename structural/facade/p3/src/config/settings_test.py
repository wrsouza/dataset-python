"""Test settings — uses SQLite in-memory so no Postgres server is needed."""

from __future__ import annotations

from config.settings import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
