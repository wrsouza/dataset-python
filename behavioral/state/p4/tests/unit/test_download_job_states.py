"""Unit tests for the DownloadJob State pattern implementation."""

from __future__ import annotations

import pytest

from download_manager_fsm.domain.entities import DownloadJob
from download_manager_fsm.domain.interfaces import InvalidTransitionError


def test_new_job_starts_idle() -> None:
    job = DownloadJob(job_id="j1", s3_key="bucket/file.zip")

    assert job.get_current_state_name() == "Idle"
    assert job.get_allowed_transitions() == ["start"]


def test_start_transitions_to_downloading() -> None:
    job = DownloadJob(job_id="j1", s3_key="bucket/file.zip")

    job.start()

    assert job.get_current_state_name() == "Downloading"


def test_pause_then_resume_returns_to_downloading() -> None:
    job = DownloadJob(job_id="j1", s3_key="bucket/file.zip")
    job.start()

    job.pause()
    assert job.get_current_state_name() == "Paused"

    job.resume()
    assert job.get_current_state_name() == "Downloading"


def test_complete_records_bytes_and_transitions_to_completed() -> None:
    job = DownloadJob(job_id="j1", s3_key="bucket/file.zip")
    job.start()

    job.complete(1024)

    assert job.get_current_state_name() == "Completed"
    assert job.bytes_downloaded == 1024
    assert job.get_allowed_transitions() == []


def test_fail_records_reason_and_transitions_to_failed() -> None:
    job = DownloadJob(job_id="j1", s3_key="bucket/file.zip")
    job.start()

    job.fail("connection reset")

    assert job.get_current_state_name() == "Failed"
    assert job.failure_reason == "connection reset"


def test_retry_from_failed_returns_to_idle() -> None:
    job = DownloadJob(job_id="j1", s3_key="bucket/file.zip")
    job.start()
    job.fail("connection reset")

    job.retry()

    assert job.get_current_state_name() == "Idle"


def test_retry_from_paused_returns_to_idle() -> None:
    job = DownloadJob(job_id="j1", s3_key="bucket/file.zip")
    job.start()
    job.pause()

    job.retry()

    assert job.get_current_state_name() == "Idle"


def test_idle_rejects_pause() -> None:
    job = DownloadJob(job_id="j1", s3_key="bucket/file.zip")

    with pytest.raises(InvalidTransitionError):
        job.pause()


def test_completed_is_terminal() -> None:
    job = DownloadJob(job_id="j1", s3_key="bucket/file.zip")
    job.start()
    job.complete(1024)

    with pytest.raises(InvalidTransitionError):
        job.retry()


def test_history_records_each_transition() -> None:
    job = DownloadJob(job_id="j1", s3_key="bucket/file.zip")

    job.start()
    job.pause()

    assert [record.action for record in job.history] == ["start", "pause"]
