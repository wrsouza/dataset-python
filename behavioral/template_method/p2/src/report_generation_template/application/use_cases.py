"""Application use cases for the Report Generation Template.

Each use case has a single responsibility and depends only on
abstractions (DIP): the generator registry and the report repository.
"""

from __future__ import annotations

from report_generation_template.application.generators.registry import get_generator
from report_generation_template.domain.entities import ReportRequest, ReportResult
from report_generation_template.infrastructure.repository import (
    InMemoryReportRepository,
)


class GenerateReportUseCase:
    def __init__(self, repository: InMemoryReportRepository) -> None:
        self._repository = repository

    def execute(self, format_name: str, request: ReportRequest) -> ReportResult:
        generator = get_generator(format_name)
        result = generator.generate(request.title, request.rows)
        self._repository.save(result)
        return result


class GetReportUseCase:
    def __init__(self, repository: InMemoryReportRepository) -> None:
        self._repository = repository

    def execute(self, report_id: str) -> ReportResult:
        return self._repository.find_by_id(report_id)
