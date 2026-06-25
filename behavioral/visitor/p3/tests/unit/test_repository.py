"""Unit tests for DjangoExportJobRepository, against a real (in-memory
SQLite) ORM."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from content_export_visitor.domain.entities import ExportJob
from content_export_visitor.domain.exceptions import ExportJobNotFoundError
from content_export_visitor.infrastructure.repository import DjangoExportJobRepository

pytestmark = pytest.mark.django_db


def test_save_and_find_by_id_round_trips_job() -> None:
    repository = DjangoExportJobRepository()
    job = ExportJob(
        job_id="j1",
        format_name="json",
        s3_key="exports/j1.json",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    repository.save(job)

    found = repository.find_by_id("j1")
    assert found.s3_key == "exports/j1.json"


def test_find_by_id_raises_for_unknown_job() -> None:
    repository = DjangoExportJobRepository()

    with pytest.raises(ExportJobNotFoundError):
        repository.find_by_id("unknown")
