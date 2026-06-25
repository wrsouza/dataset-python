"""Core entities for the scheduled command executor domain."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class ExecutionStatus(StrEnum):
    """Outcome of dispatching a command to a Celery worker."""

    SUCCESS = "success"
    FAILURE = "failure"


@dataclass
class ExecutionRecord:
    """A historical entry describing the outcome of executing one command."""

    job_id: str
    command_name: str
    status: ExecutionStatus
    result_message: str
    executed_at: datetime
