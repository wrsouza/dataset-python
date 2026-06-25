"""Unit tests for the Download Manager use cases."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from download_manager_fsm.application.use_cases import (
    CompleteDownloadUseCase,
    DownloadJobNotFoundError,
    FailDownloadUseCase,
    GetDownloadJobUseCase,
    PauseDownloadUseCase,
    ResumeDownloadUseCase,
    RetryDownloadUseCase,
    StartDownloadInput,
    StartDownloadUseCase,
)
from download_manager_fsm.domain.interfaces import InvalidTransitionError
from download_manager_fsm.infrastructure.sqlite_repository import (
    SqliteDownloadJobRepository,
)


class FakeS3Client:
    def __init__(self, content_length: int = 1024) -> None:
        self.content_length = content_length
        self.head_object_calls: list[tuple[str, str]] = []

    def head_object(self, Bucket: str, Key: str) -> dict[str, object]:
        self.head_object_calls.append((Bucket, Key))
        return {"ContentLength": self.content_length}


@pytest.fixture
def repository() -> Iterator[SqliteDownloadJobRepository]:
    connection = sqlite3.connect(":memory:")
    try:
        yield SqliteDownloadJobRepository(connection)
    finally:
        connection.close()


def test_start_creates_and_persists_a_new_job(
    repository: SqliteDownloadJobRepository,
) -> None:
    use_case = StartDownloadUseCase(repository)

    job = use_case.execute(StartDownloadInput(job_id="j1", s3_key="bucket/file.zip"))

    assert job.get_current_state_name() == "Downloading"
    assert repository.find_by_id("j1") is not None


def test_pause_use_case_persists_transition(
    repository: SqliteDownloadJobRepository,
) -> None:
    StartDownloadUseCase(repository).execute(
        StartDownloadInput(job_id="j1", s3_key="bucket/file.zip")
    )

    job = PauseDownloadUseCase(repository).execute("j1")

    assert job.get_current_state_name() == "Paused"


def test_pause_unknown_job_raises(repository: SqliteDownloadJobRepository) -> None:
    with pytest.raises(DownloadJobNotFoundError):
        PauseDownloadUseCase(repository).execute("unknown")


def test_resume_use_case_persists_transition(
    repository: SqliteDownloadJobRepository,
) -> None:
    StartDownloadUseCase(repository).execute(
        StartDownloadInput(job_id="j1", s3_key="bucket/file.zip")
    )
    PauseDownloadUseCase(repository).execute("j1")

    job = ResumeDownloadUseCase(repository).execute("j1")

    assert job.get_current_state_name() == "Downloading"


def test_complete_use_case_fetches_size_from_s3(
    repository: SqliteDownloadJobRepository,
) -> None:
    StartDownloadUseCase(repository).execute(
        StartDownloadInput(job_id="j1", s3_key="my-bucket/file.zip")
    )
    s3_client = FakeS3Client(content_length=2048)

    job = CompleteDownloadUseCase(repository, s3_client).execute("j1")

    assert job.get_current_state_name() == "Completed"
    assert job.bytes_downloaded == 2048
    assert s3_client.head_object_calls == [("my-bucket", "file.zip")]


def test_fail_use_case_records_reason(repository: SqliteDownloadJobRepository) -> None:
    StartDownloadUseCase(repository).execute(
        StartDownloadInput(job_id="j1", s3_key="bucket/file.zip")
    )

    job = FailDownloadUseCase(repository).execute("j1", "connection reset")

    assert job.get_current_state_name() == "Failed"
    assert job.failure_reason == "connection reset"


def test_retry_use_case_resets_to_idle(repository: SqliteDownloadJobRepository) -> None:
    StartDownloadUseCase(repository).execute(
        StartDownloadInput(job_id="j1", s3_key="bucket/file.zip")
    )
    FailDownloadUseCase(repository).execute("j1", "timeout")

    job = RetryDownloadUseCase(repository).execute("j1")

    assert job.get_current_state_name() == "Idle"


def test_invalid_transition_raises(repository: SqliteDownloadJobRepository) -> None:
    StartDownloadUseCase(repository).execute(
        StartDownloadInput(job_id="j1", s3_key="bucket/file.zip")
    )

    with pytest.raises(InvalidTransitionError):
        ResumeDownloadUseCase(repository).execute("j1")


def test_get_download_job_use_case_returns_none_for_unknown(
    repository: SqliteDownloadJobRepository,
) -> None:
    assert GetDownloadJobUseCase(repository).execute("unknown") is None
