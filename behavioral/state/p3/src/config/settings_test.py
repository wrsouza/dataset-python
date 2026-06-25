"""Test settings — uses an in-memory SQLite database and an eager Celery app.

Setting CELERY_TASK_ALWAYS_EAGER before `workflow_approval_fsm.infrastructure.
celery_app` is first imported lets the test suite dispatch notification
tasks synchronously, without a real Redis broker or worker process.
"""

from __future__ import annotations

import os

os.environ["CELERY_TASK_ALWAYS_EAGER"] = "true"

from config.settings import *  # noqa: F401, F403, E402

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
