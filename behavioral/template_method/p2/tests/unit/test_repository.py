"""Unit tests for InMemoryReportRepository."""

from __future__ import annotations

import pytest

from report_generation_template.domain.entities import ReportResult
from report_generation_template.domain.exceptions import ReportNotFoundError
from report_generation_template.infrastructure.repository import (
    InMemoryReportRepository,
)


def test_save_and_find_by_id_round_trips_report() -> None:
    repository = InMemoryReportRepository()
    result = ReportResult(
        report_id="r1", format_name="csv", content="data", row_count=1
    )

    repository.save(result)

    assert repository.find_by_id("r1") == result


def test_find_by_id_raises_for_unknown_report() -> None:
    repository = InMemoryReportRepository()

    with pytest.raises(ReportNotFoundError):
        repository.find_by_id("unknown")
