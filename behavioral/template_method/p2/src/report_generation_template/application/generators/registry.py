"""Generator registry — maps string keys to ReportGenerator instances."""

from __future__ import annotations

from report_generation_template.application.generators.csv_generator import (
    CSVReportGenerator,
)
from report_generation_template.application.generators.html_generator import (
    HTMLReportGenerator,
)
from report_generation_template.application.generators.json_generator import (
    JSONReportGenerator,
)
from report_generation_template.domain.exceptions import InvalidFormatError
from report_generation_template.domain.interfaces import ReportGenerator

_GENERATOR_MAP: dict[str, ReportGenerator] = {
    "csv": CSVReportGenerator(),
    "json": JSONReportGenerator(),
    "html": HTMLReportGenerator(),
}


def get_generator(name: str) -> ReportGenerator:
    """Resolve a generator by format name.

    Raises:
        InvalidFormatError: when name is not registered.
    """
    generator = _GENERATOR_MAP.get(name.lower())
    if generator is None:
        raise InvalidFormatError(name)
    return generator


def list_format_names() -> list[str]:
    return sorted(_GENERATOR_MAP)
