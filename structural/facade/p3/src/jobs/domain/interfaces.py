"""Abstract interfaces (ports) for the background job subsystem.

These ABCs define the contract that infrastructure adapters (Celery/Redis,
or fakes used in tests) must satisfy. The application layer (the Facade)
depends only on these abstractions — never on Celery or Redis directly —
fulfilling the Dependency Inversion Principle.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from jobs.domain.entities import JobInfo, JobRequest


class AbstractTaskQueue(ABC):
    """Port for enqueueing and cancelling background jobs."""

    @abstractmethod
    def enqueue(self, request: JobRequest) -> str:
        """Submit a job for asynchronous execution and return its job id."""

    @abstractmethod
    def cancel(self, job_id: str) -> bool:
        """Request cancellation of a queued or running job."""

    @abstractmethod
    def retry(self, job_id: str) -> str:
        """Re-submit a failed job and return the new job id."""


class AbstractJobStatusReader(ABC):
    """Port for querying the current state of a background job."""

    @abstractmethod
    def get_status(self, job_id: str) -> JobInfo:
        """Return the current snapshot of a job by its id."""


class AbstractJobRepository(ABC):
    """Port for persisting job submission metadata."""

    @abstractmethod
    def save(self, job: JobInfo) -> None:
        """Persist or update a job record."""

    @abstractmethod
    def find_by_id(self, job_id: str) -> JobInfo | None:
        """Look up a previously persisted job record."""
