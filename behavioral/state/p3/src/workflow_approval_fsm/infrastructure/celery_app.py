"""Celery application instance and the notification task.

Dispatched after every workflow state transition; runs in a worker
process and never knows about the State pattern — only the
`request_id` and a human-readable `message` to log.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime

from celery import Celery

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

app = Celery(
    "workflow_approval_fsm",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)
app.conf.task_track_started = True
app.conf.task_always_eager = (
    os.environ.get("CELERY_TASK_ALWAYS_EAGER", "false").lower() == "true"
)
app.conf.task_eager_propagates = app.conf.task_always_eager


@app.task(name="workflow_approval_fsm.notify")  # type: ignore[untyped-decorator]
def notify_task(request_id: str, message: str) -> str:
    """Write a notification log entry for a workflow request transition."""
    from workflow_approval_fsm.django_app.models import NotificationLogModel

    NotificationLogModel.objects.create(
        request_id=request_id, message=message, created_at=datetime.now(UTC)
    )
    return message
