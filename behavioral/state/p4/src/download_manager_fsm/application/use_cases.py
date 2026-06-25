"""Application use cases for the Download Manager State machine.

Each use case loads the job (or creates it, for `start`), delegates to
the FSM, and persists the result. `CompleteDownloadUseCase` is the only
one that talks to S3 — it confirms the object exists via `head_object`
and records its size, simulating "the transfer finished".
"""

from __future__ import annotations

from dataclasses import dataclass

from download_manager_fsm.domain.entities import DownloadJob
from download_manager_fsm.infrastructure.factory import S3ClientLike
from download_manager_fsm.infrastructure.sqlite_repository import (
    SqliteDownloadJobRepository,
)


class DownloadJobNotFoundError(Exception):
    def __init__(self, job_id: str) -> None:
        super().__init__(f"Download job '{job_id}' not found")
        self.job_id = job_id


@dataclass
class StartDownloadInput:
    job_id: str
    s3_key: str


class StartDownloadUseCase:
    def __init__(self, repository: SqliteDownloadJobRepository) -> None:
        self._repository = repository

    def execute(self, data: StartDownloadInput) -> DownloadJob:
        job = self._repository.find_by_id(data.job_id) or DownloadJob(
            job_id=data.job_id, s3_key=data.s3_key
        )
        job.start()
        self._repository.save(job)
        return job


class PauseDownloadUseCase:
    def __init__(self, repository: SqliteDownloadJobRepository) -> None:
        self._repository = repository

    def execute(self, job_id: str) -> DownloadJob:
        job = self._load(job_id)
        job.pause()
        self._repository.save(job)
        return job

    def _load(self, job_id: str) -> DownloadJob:
        job = self._repository.find_by_id(job_id)
        if job is None:
            raise DownloadJobNotFoundError(job_id)
        return job


class ResumeDownloadUseCase:
    def __init__(self, repository: SqliteDownloadJobRepository) -> None:
        self._repository = repository

    def execute(self, job_id: str) -> DownloadJob:
        job = self._repository.find_by_id(job_id)
        if job is None:
            raise DownloadJobNotFoundError(job_id)
        job.resume()
        self._repository.save(job)
        return job


class CompleteDownloadUseCase:
    def __init__(
        self, repository: SqliteDownloadJobRepository, s3_client: S3ClientLike
    ) -> None:
        self._repository = repository
        self._s3_client = s3_client

    def execute(self, job_id: str) -> DownloadJob:
        job = self._repository.find_by_id(job_id)
        if job is None:
            raise DownloadJobNotFoundError(job_id)

        bucket, _, key = job.s3_key.partition("/")
        head = self._s3_client.head_object(Bucket=bucket, Key=key)
        content_length = int(str(head.get("ContentLength", 0)))

        job.complete(content_length)
        self._repository.save(job)
        return job


class FailDownloadUseCase:
    def __init__(self, repository: SqliteDownloadJobRepository) -> None:
        self._repository = repository

    def execute(self, job_id: str, reason: str) -> DownloadJob:
        job = self._repository.find_by_id(job_id)
        if job is None:
            raise DownloadJobNotFoundError(job_id)
        job.fail(reason)
        self._repository.save(job)
        return job


class RetryDownloadUseCase:
    def __init__(self, repository: SqliteDownloadJobRepository) -> None:
        self._repository = repository

    def execute(self, job_id: str) -> DownloadJob:
        job = self._repository.find_by_id(job_id)
        if job is None:
            raise DownloadJobNotFoundError(job_id)
        job.retry()
        self._repository.save(job)
        return job


class GetDownloadJobUseCase:
    def __init__(self, repository: SqliteDownloadJobRepository) -> None:
        self._repository = repository

    def execute(self, job_id: str) -> DownloadJob | None:
        return self._repository.find_by_id(job_id)
