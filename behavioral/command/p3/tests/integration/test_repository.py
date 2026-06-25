"""Integration tests for DjangoExecutionRepository against a real ORM."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from scheduled_executor.domain.entities import ExecutionRecord, ExecutionStatus
from scheduled_executor.infrastructure.repository import DjangoExecutionRepository

pytestmark = pytest.mark.django_db


def _record() -> ExecutionRecord:
    return ExecutionRecord(
        job_id="job-1",
        command_name="backup",
        status=ExecutionStatus.SUCCESS,
        result_message="Backup of 'orders-db' completed",
        executed_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_save_and_get_round_trips_record() -> None:
    repository = DjangoExecutionRepository()

    repository.save(_record())
    fetched = repository.get("job-1")

    assert fetched is not None
    assert fetched.status == ExecutionStatus.SUCCESS
    assert fetched.result_message == "Backup of 'orders-db' completed"


def test_get_returns_none_when_missing() -> None:
    repository = DjangoExecutionRepository()

    assert repository.get("unknown") is None


def test_save_updates_existing_record() -> None:
    repository = DjangoExecutionRepository()
    repository.save(_record())

    updated = _record()
    updated.status = ExecutionStatus.FAILURE
    updated.result_message = "boom"
    repository.save(updated)

    fetched = repository.get("job-1")
    assert fetched is not None
    assert fetched.status == ExecutionStatus.FAILURE
