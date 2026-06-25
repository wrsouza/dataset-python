"""Domain entities and value objects for the background job subsystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class JobStatus(StrEnum):
    """Lifecycle states of a background job."""

    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    REVOKED = "REVOKED"
    RETRY = "RETRY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class JobRequest:
    """Value object describing a job submission request."""

    task_name: str
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    max_retries: int = 3


@dataclass(frozen=True)
class JobInfo:
    """Snapshot of a background job at a point in time."""

    job_id: str
    task_name: str
    status: JobStatus
    created_at: datetime
    result: Any = None
    error_message: str | None = None
    retries: int = 0
