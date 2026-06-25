"""Unit tests for JobFacade — pure in-memory fakes, no Celery/Redis/Django DB."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from jobs.application.facade import JobFacade, JobNotFoundError
from jobs.domain.entities import JobInfo, JobRequest, JobStatus
from jobs.domain.interfaces import (
    AbstractJobRepository,
    AbstractJobStatusReader,
    AbstractTaskQueue,
)


class FakeTaskQueue(AbstractTaskQueue):
    """In-memory fake replacing Celery for unit tests."""

    def __init__(self) -> None:
        self.enqueued: list[JobRequest] = []
        self.cancelled: list[str] = []
        self.next_id = 1

    def enqueue(self, request: JobRequest) -> str:
        self.enqueued.append(request)
        job_id = f"job-{self.next_id}"
        self.next_id += 1
        return job_id

    def cancel(self, job_id: str) -> bool:
        self.cancelled.append(job_id)
        return True

    def retry(self, job_id: str) -> str:
        return f"{job_id}-retry"


class FakeStatusReader(AbstractJobStatusReader):
    """In-memory fake status reader, configurable per test."""

    def __init__(self) -> None:
        self.statuses: dict[str, JobInfo] = {}

    def get_status(self, job_id: str) -> JobInfo:
        if job_id in self.statuses:
            return self.statuses[job_id]
        return JobInfo(
            job_id=job_id,
            task_name="",
            status=JobStatus.UNKNOWN,
            created_at=datetime.now(UTC),
        )


class FakeRepository(AbstractJobRepository):
    """In-memory fake repository replacing the Django ORM for unit tests."""

    def __init__(self) -> None:
        self._store: dict[str, JobInfo] = {}

    def save(self, job: JobInfo) -> None:
        self._store[job.job_id] = job

    def find_by_id(self, job_id: str) -> JobInfo | None:
        return self._store.get(job_id)


@pytest.fixture
def queue() -> FakeTaskQueue:
    return FakeTaskQueue()


@pytest.fixture
def reader() -> FakeStatusReader:
    return FakeStatusReader()


@pytest.fixture
def repository() -> FakeRepository:
    return FakeRepository()


@pytest.fixture
def facade(
    queue: FakeTaskQueue, reader: FakeStatusReader, repository: FakeRepository
) -> JobFacade:
    return JobFacade(task_queue=queue, status_reader=reader, repository=repository)


class TestSchedule:
    def test_schedule_enqueues_and_persists_pending_job(
        self, facade: JobFacade, queue: FakeTaskQueue, repository: FakeRepository
    ) -> None:
        request = JobRequest(
            task_name="jobs.send_report", kwargs={"recipient": "a@b.com"}
        )
        job = facade.schedule(request)

        assert job.status is JobStatus.PENDING
        assert job.task_name == "jobs.send_report"
        assert queue.enqueued == [request]
        assert repository.find_by_id(job.job_id) == job

    def test_schedule_returns_unique_job_ids(self, facade: JobFacade) -> None:
        request = JobRequest(task_name="jobs.process_dataset")
        first = facade.schedule(request)
        second = facade.schedule(request)
        assert first.job_id != second.job_id


class TestGetStatus:
    def test_get_status_returns_live_status_and_persists_it(
        self,
        facade: JobFacade,
        reader: FakeStatusReader,
        repository: FakeRepository,
    ) -> None:
        reader.statuses["job-1"] = JobInfo(
            job_id="job-1",
            task_name="jobs.send_report",
            status=JobStatus.SUCCESS,
            created_at=datetime.now(UTC),
            result={"sent": True},
        )
        job = facade.get_status("job-1")
        assert job.status is JobStatus.SUCCESS
        assert repository.find_by_id("job-1") is not None

    def test_get_status_falls_back_to_repository_when_unknown(
        self, facade: JobFacade, repository: FakeRepository
    ) -> None:
        persisted = JobInfo(
            job_id="job-2",
            task_name="jobs.send_report",
            status=JobStatus.SUCCESS,
            created_at=datetime.now(UTC),
        )
        repository.save(persisted)
        job = facade.get_status("job-2")
        assert job == persisted

    def test_get_status_raises_when_job_never_existed(self, facade: JobFacade) -> None:
        with pytest.raises(JobNotFoundError):
            facade.get_status("missing-job")


class TestCancel:
    def test_cancel_marks_job_revoked_in_repository(
        self, facade: JobFacade, queue: FakeTaskQueue, repository: FakeRepository
    ) -> None:
        request = JobRequest(task_name="jobs.send_report")
        job = facade.schedule(request)

        cancelled = facade.cancel(job.job_id)

        assert cancelled is True
        assert queue.cancelled == [job.job_id]
        assert repository.find_by_id(job.job_id).status is JobStatus.REVOKED  # type: ignore[union-attr]

    def test_cancel_unknown_job_still_marks_revoked(
        self, facade: JobFacade, repository: FakeRepository
    ) -> None:
        facade.cancel("never-scheduled")
        record = repository.find_by_id("never-scheduled")
        assert record is not None
        assert record.status is JobStatus.REVOKED


class TestRetry:
    def test_retry_resubmits_and_increments_retry_count(
        self, facade: JobFacade, repository: FakeRepository
    ) -> None:
        request = JobRequest(task_name="jobs.process_dataset")
        original = facade.schedule(request)

        retried = facade.retry(original.job_id)

        assert retried.job_id == f"{original.job_id}-retry"
        assert retried.status is JobStatus.RETRY
        assert retried.retries == 1
        assert repository.find_by_id(retried.job_id) == retried

    def test_retry_unknown_job_uses_empty_task_name(self, facade: JobFacade) -> None:
        retried = facade.retry("ghost-job")
        assert retried.task_name == ""
        assert retried.retries == 1
