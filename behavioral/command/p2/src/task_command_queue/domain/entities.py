"""Core entities for the task queue domain."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class TaskStatus(StrEnum):
    """Lifecycle state of an enqueued task."""

    QUEUED = "queued"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskRecord:
    """A historical entry describing the outcome of executing one command."""

    task_id: str
    command_name: str
    status: TaskStatus
    result_message: str
    executed_at: datetime
