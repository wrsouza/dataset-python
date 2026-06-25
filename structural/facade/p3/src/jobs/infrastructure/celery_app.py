"""Celery application instance and demo task definitions."""

from __future__ import annotations

import os
import time
from typing import Any

from celery import Celery

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

app = Celery(
    "jobs",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)
app.conf.task_default_max_retries = 3
app.conf.task_track_started = True


@app.task(name="jobs.send_report", bind=True, max_retries=3)  # type: ignore[untyped-decorator]
def send_report(self: Any, recipient: str, report_id: str) -> dict[str, str]:
    """Simulate generation and delivery of a report (demo Celery task)."""
    time.sleep(0.1)
    return {"recipient": recipient, "report_id": report_id, "status": "sent"}


@app.task(name="jobs.process_dataset", bind=True, max_retries=3)  # type: ignore[untyped-decorator]
def process_dataset(self: Any, dataset_id: str) -> dict[str, str]:
    """Simulate a long-running dataset processing job (demo Celery task)."""
    time.sleep(0.1)
    return {"dataset_id": dataset_id, "status": "processed"}
