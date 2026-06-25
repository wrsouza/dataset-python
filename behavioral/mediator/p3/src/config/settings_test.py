"""Test settings — SQLite in-memory DB and an in-process channel layer.

Neither a real PostgreSQL server nor a real Redis instance is needed to
run the test suite.
"""

from __future__ import annotations

from config.settings import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}
