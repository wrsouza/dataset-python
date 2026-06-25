"""Abstractions for the Command pattern and its persistence boundary."""

from __future__ import annotations

from abc import ABC, abstractmethod

from scheduled_executor.domain.entities import ExecutionRecord


class ScheduledCommand(ABC):
    """Encapsulates a single scheduled unit of work as an object.

    Adding a new scheduled task type requires only a new subclass — no
    changes to the Celery task or the use cases (OCP).
    """

    @abstractmethod
    def execute(self) -> str:
        """Perform the task against its receiver and return a result message."""

    @abstractmethod
    def get_command_name(self) -> str:
        """Return the stable name used to identify this command type."""


class ExecutionRepository(ABC):
    """Persistence boundary for execution records."""

    @abstractmethod
    def save(self, record: ExecutionRecord) -> None:
        """Persist an execution record."""

    @abstractmethod
    def get(self, job_id: str) -> ExecutionRecord | None:
        """Retrieve an execution record by its job id, if it exists."""
