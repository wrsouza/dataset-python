"""Unit tests for SqliteDownloadJobRepository."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from download_manager_fsm.domain.entities import DownloadJob
from download_manager_fsm.infrastructure.sqlite_repository import (
    SqliteDownloadJobRepository,
)


@pytest.fixture
def repository() -> Iterator[SqliteDownloadJobRepository]:
    connection = sqlite3.connect(":memory:")
    try:
        yield SqliteDownloadJobRepository(connection)
    finally:
        connection.close()


def test_save_and_find_round_trips_state(
    repository: SqliteDownloadJobRepository,
) -> None:
    job = DownloadJob(job_id="j1", s3_key="bucket/file.zip")
    job.start()
    repository.save(job)

    found = repository.find_by_id("j1")

    assert found is not None
    assert found.s3_key == "bucket/file.zip"
    assert found.get_current_state_name() == "Downloading"


def test_find_returns_none_for_unknown_job(
    repository: SqliteDownloadJobRepository,
) -> None:
    assert repository.find_by_id("unknown") is None


def test_save_overwrites_existing_job_state(
    repository: SqliteDownloadJobRepository,
) -> None:
    job = DownloadJob(job_id="j1", s3_key="bucket/file.zip")
    repository.save(job)

    job.start()
    job.complete(2048)
    repository.save(job)

    found = repository.find_by_id("j1")
    assert found is not None
    assert found.get_current_state_name() == "Completed"
    assert found.bytes_downloaded == 2048


def test_save_persists_failure_reason(repository: SqliteDownloadJobRepository) -> None:
    job = DownloadJob(job_id="j1", s3_key="bucket/file.zip")
    job.start()
    job.fail("timeout")
    repository.save(job)

    found = repository.find_by_id("j1")
    assert found is not None
    assert found.failure_reason == "timeout"
