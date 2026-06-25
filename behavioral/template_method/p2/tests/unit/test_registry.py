"""Unit tests for the generator registry."""

from __future__ import annotations

import pytest

from report_generation_template.application.generators.csv_generator import (
    CSVReportGenerator,
)
from report_generation_template.application.generators.registry import (
    get_generator,
    list_format_names,
)
from report_generation_template.domain.exceptions import InvalidFormatError


def test_get_generator_resolves_csv() -> None:
    generator = get_generator("csv")

    assert isinstance(generator, CSVReportGenerator)


def test_get_generator_is_case_insensitive() -> None:
    generator = get_generator("JSON")

    assert generator.get_format_name() == "json"


def test_get_generator_raises_for_unknown_format() -> None:
    with pytest.raises(InvalidFormatError):
        get_generator("pdf")


def test_list_format_names_includes_all_registered() -> None:
    assert list_format_names() == ["csv", "html", "json"]
