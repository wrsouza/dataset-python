"""Unit tests for the Report Generation Template use cases."""

from __future__ import annotations

import pytest

from report_generation_template.application.use_cases import (
    GenerateReportUseCase,
    GetReportUseCase,
)
from report_generation_template.domain.entities import ReportRequest
from report_generation_template.domain.exceptions import (
    InvalidFormatError,
    ReportNotFoundError,
)
from report_generation_template.infrastructure.repository import (
    InMemoryReportRepository,
)


def test_generate_report_use_case_persists_result() -> None:
    repository = InMemoryReportRepository()
    use_case = GenerateReportUseCase(repository)

    result = use_case.execute("csv", ReportRequest(title="Users", rows=[{"id": 1}]))

    assert repository.find_by_id(result.report_id) == result


def test_generate_report_use_case_raises_for_unknown_format() -> None:
    use_case = GenerateReportUseCase(InMemoryReportRepository())

    with pytest.raises(InvalidFormatError):
        use_case.execute("pdf", ReportRequest(title="Users", rows=[]))


def test_get_report_use_case_returns_saved_report() -> None:
    repository = InMemoryReportRepository()
    generate = GenerateReportUseCase(repository)
    result = generate.execute("json", ReportRequest(title="Users", rows=[]))

    fetched = GetReportUseCase(repository).execute(result.report_id)

    assert fetched == result


def test_get_report_use_case_raises_for_unknown_id() -> None:
    use_case = GetReportUseCase(InMemoryReportRepository())

    with pytest.raises(ReportNotFoundError):
        use_case.execute("unknown")
