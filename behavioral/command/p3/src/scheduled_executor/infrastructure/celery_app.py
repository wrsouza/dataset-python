"""Celery application instance and the command-dispatch task."""

from __future__ import annotations

import os

from celery import Celery

from scheduled_executor.infrastructure.commands import build_command

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

app = Celery(
    "scheduled_executor",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)
app.conf.task_track_started = True
app.conf.task_always_eager = (
    os.environ.get("CELERY_TASK_ALWAYS_EAGER", "false").lower() == "true"
)
app.conf.task_eager_propagates = app.conf.task_always_eager


@app.task(name="scheduled_executor.run_command")  # type: ignore[untyped-decorator]
def run_command_task(command_name: str, payload: dict[str, object]) -> str:
    """Build the named command from its payload and execute it.

    This is the Invoker boundary that runs inside the Celery worker
    process: it never knows what a command does internally, only the
    ScheduledCommand contract (execute / get_command_name).
    """
    command = build_command(command_name, payload)
    return command.execute()
