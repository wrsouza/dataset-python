"""Use cases orchestrating command dispatch through Celery and persistence."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Protocol

from scheduled_executor.domain.entities import ExecutionRecord, ExecutionStatus
from scheduled_executor.domain.interfaces import ExecutionRepository
from scheduled_executor.infrastructure.commands import build_command


class ExecutionNotFoundError(Exception):
    """Raised when a job id has no matching execution record."""


class CommandTask(Protocol):
    """Contract for the Celery task that dispatches a command to a worker."""

    def delay(
        self, command_name: str, payload: dict[str, object]
    ) -> AsyncResultLike: ...


class AsyncResultLike(Protocol):
    """Contract for the Celery AsyncResult this use case relies on."""

    def get(self, timeout: float) -> str: ...


class TriggerCommandUseCase:
    """Validates and dispatches a command to Celery, persisting the outcome."""

    def __init__(self, task: CommandTask, repository: ExecutionRepository) -> None:
        self._task = task
        self._repository = repository

    def execute(self, command_name: str, payload: dict[str, object]) -> ExecutionRecord:
        build_command(command_name, payload)  # validates name and payload eagerly

        job_id = str(uuid.uuid4())
        try:
            result_message = self._task.delay(command_name, payload).get(timeout=10.0)
            status = ExecutionStatus.SUCCESS
        except Exception as exc:  # any worker failure becomes a FAILURE record
            result_message = str(exc)
            status = ExecutionStatus.FAILURE

        record = ExecutionRecord(
            job_id=job_id,
            command_name=command_name,
            status=status,
            result_message=result_message,
            executed_at=datetime.now(UTC),
        )
        self._repository.save(record)
        return record


class GetExecutionUseCase:
    """Fetches a previously dispatched command's execution record by job id."""

    def __init__(self, repository: ExecutionRepository) -> None:
        self._repository = repository

    def execute(self, job_id: str) -> ExecutionRecord:
        record = self._repository.get(job_id)
        if record is None:
            raise ExecutionNotFoundError(f"Execution {job_id} not found")
        return record
