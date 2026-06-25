"""Integration tests for jobs Django views using SQLite in-memory DB.

Celery's broker/result-backend calls are mocked so the suite never touches
a real Redis instance — the JobFacade composition is still exercised end
to end through the Django test client.
"""

from __future__ import annotations

import json

# Django must be configured before importing models.
import os
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import django
from django.test import Client, TestCase

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")
django.setup()

from jobs.django_app.models import JobRecord  # noqa: E402
from jobs.domain.entities import JobInfo, JobStatus  # noqa: E402


class ScheduleJobViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_schedule_job_returns_201_and_persists_record(self) -> None:
        with patch("jobs.django_app.views.build_job_facade") as mock_build_facade:
            mock_facade = MagicMock()
            mock_facade.schedule.return_value = JobInfo(
                job_id="celery-task-id-1",
                task_name="jobs.send_report",
                status=JobStatus.PENDING,
                created_at=datetime.now(UTC),
            )
            mock_build_facade.return_value = mock_facade

            resp = self.client.post(
                "/jobs/",
                data=json.dumps(
                    {
                        "task_name": "jobs.send_report",
                        "kwargs": {"recipient": "a@b.com", "report_id": "r1"},
                    }
                ),
                content_type="application/json",
            )

        assert resp.status_code == 201
        body = json.loads(resp.content)
        assert body["job_id"] == "celery-task-id-1"
        assert body["status"] == "PENDING"

    def test_schedule_job_rejects_unknown_task_name(self) -> None:
        resp = self.client.post(
            "/jobs/",
            data=json.dumps({"task_name": "not.a.real.task"}),
            content_type="application/json",
        )
        assert resp.status_code == 400


class JobStatusViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        JobRecord.objects.create(
            job_id="job-xyz",
            task_name="jobs.process_dataset",
            status="SUCCESS",
            result={"dataset_id": "d1", "status": "processed"},
            retries=0,
        )

    def test_get_status_returns_200_with_job_payload(self) -> None:
        with patch("jobs.django_app.views.build_job_facade") as mock_build_facade:
            mock_facade = MagicMock()
            mock_facade.get_status.return_value = JobInfo(
                job_id="job-xyz",
                task_name="jobs.process_dataset",
                status=JobStatus.SUCCESS,
                created_at=datetime.now(UTC),
                result={"dataset_id": "d1", "status": "processed"},
            )
            mock_build_facade.return_value = mock_facade

            resp = self.client.get("/jobs/job-xyz/")

        assert resp.status_code == 200
        body = json.loads(resp.content)
        assert body["status"] == "SUCCESS"
        assert body["result"]["dataset_id"] == "d1"

    def test_get_status_returns_404_for_unknown_job(self) -> None:
        from jobs.application.facade import JobNotFoundError

        with patch("jobs.django_app.views.build_job_facade") as mock_build_facade:
            mock_facade = MagicMock()
            mock_facade.get_status.side_effect = JobNotFoundError("nope")
            mock_build_facade.return_value = mock_facade

            resp = self.client.get("/jobs/does-not-exist/")

        assert resp.status_code == 404


class CancelJobViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_cancel_job_returns_cancellation_flag(self) -> None:
        with patch("jobs.django_app.views.build_job_facade") as mock_build_facade:
            mock_facade = MagicMock()
            mock_facade.cancel.return_value = True
            mock_build_facade.return_value = mock_facade

            resp = self.client.post("/jobs/job-abc/cancel/")

        assert resp.status_code == 200
        body = json.loads(resp.content)
        assert body == {"job_id": "job-abc", "cancelled": True}


class RetryJobViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_retry_job_returns_new_job_info(self) -> None:
        with patch("jobs.django_app.views.build_job_facade") as mock_build_facade:
            mock_facade = MagicMock()
            mock_facade.retry.return_value = JobInfo(
                job_id="job-abc-retry",
                task_name="jobs.send_report",
                status=JobStatus.RETRY,
                created_at=datetime.now(UTC),
                retries=1,
            )
            mock_build_facade.return_value = mock_facade

            resp = self.client.post("/jobs/job-abc/retry/")

        assert resp.status_code == 201
        body = json.loads(resp.content)
        assert body["job_id"] == "job-abc-retry"
        assert body["retries"] == 1


class DjangoJobRepositoryTests(TestCase):
    """Exercises the real ORM-backed repository adapter against SQLite."""

    def test_save_and_find_round_trip(self) -> None:
        from jobs.infrastructure.django_job_repository import DjangoJobRepository

        repo = DjangoJobRepository()
        job = JobInfo(
            job_id="repo-job-1",
            task_name="jobs.send_report",
            status=JobStatus.SUCCESS,
            created_at=datetime.now(UTC),
            result={"sent": True},
            retries=2,
        )
        repo.save(job)

        found = repo.find_by_id("repo-job-1")
        assert found is not None
        assert found.status is JobStatus.SUCCESS
        assert found.result == {"sent": True}
        assert found.retries == 2

    def test_find_by_id_returns_none_when_missing(self) -> None:
        from jobs.infrastructure.django_job_repository import DjangoJobRepository

        repo = DjangoJobRepository()
        assert repo.find_by_id("does-not-exist") is None

    def test_save_updates_existing_record(self) -> None:
        from jobs.infrastructure.django_job_repository import DjangoJobRepository

        repo = DjangoJobRepository()
        job = JobInfo(
            job_id="repo-job-2",
            task_name="jobs.process_dataset",
            status=JobStatus.PENDING,
            created_at=datetime.now(UTC),
        )
        repo.save(job)

        updated = JobInfo(
            job_id="repo-job-2",
            task_name="jobs.process_dataset",
            status=JobStatus.SUCCESS,
            created_at=datetime.now(UTC),
            result={"done": True},
        )
        repo.save(updated)

        found = repo.find_by_id("repo-job-2")
        assert found is not None
        assert found.status is JobStatus.SUCCESS
        assert JobRecord.objects.filter(job_id="repo-job-2").count() == 1
