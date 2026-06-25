"""Unit tests for domain entities — no external dependencies."""

from __future__ import annotations

from datetime import UTC, datetime

from jobs.domain.entities import JobInfo, JobRequest, JobStatus


class TestJobRequest:
    def test_defaults_are_empty_args_and_kwargs(self) -> None:
        request = JobRequest(task_name="jobs.send_report")
        assert request.args == ()
        assert request.kwargs == {}
        assert request.max_retries == 3

    def test_custom_args_and_kwargs_are_preserved(self) -> None:
        request = JobRequest(
            task_name="jobs.process_dataset",
            args=(1, 2),
            kwargs={"dataset_id": "abc"},
            max_retries=5,
        )
        assert request.args == (1, 2)
        assert request.kwargs == {"dataset_id": "abc"}
        assert request.max_retries == 5


class TestJobInfo:
    def test_job_info_holds_status_and_metadata(self) -> None:
        job = JobInfo(
            job_id="job-1",
            task_name="jobs.send_report",
            status=JobStatus.SUCCESS,
            created_at=datetime.now(UTC),
            result={"ok": True},
        )
        assert job.status is JobStatus.SUCCESS
        assert job.result == {"ok": True}
        assert job.error_message is None
        assert job.retries == 0

    def test_job_status_values_match_celery_states(self) -> None:
        assert JobStatus.PENDING.value == "PENDING"
        assert JobStatus.SUCCESS.value == "SUCCESS"
        assert JobStatus.FAILURE.value == "FAILURE"
        assert JobStatus.REVOKED.value == "REVOKED"
