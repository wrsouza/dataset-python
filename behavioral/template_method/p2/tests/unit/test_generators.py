"""Unit tests for the concrete report generators — exercising the
Template Method skeleton shared by all of them."""

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

ROWS = [{"id": 1, "name": "Ana"}, {"id": 2, "name": "Bob"}]


def test_csv_generator_includes_header_rows_and_summary() -> None:
    result = CSVReportGenerator().generate("Users", ROWS)

    assert "# Users" in result.content
    assert "1,Ana" in result.content
    assert "Total records: 2" in result.content
    assert result.format_name == "csv"
    assert result.row_count == 2


def test_json_generator_skips_summary_via_hook() -> None:
    result = JSONReportGenerator().generate("Users", ROWS)

    assert "Total records" not in result.content
    assert '"id": 1' in result.content


def test_html_generator_overrides_assemble() -> None:
    result = HTMLReportGenerator().generate("Users", ROWS)

    assert "<h1>Users</h1>" in result.content
    assert "<tr><td>1</td><td>Ana</td></tr>" in result.content
    assert "<p>Total records: 2</p>" in result.content


def test_generate_with_empty_rows() -> None:
    result = CSVReportGenerator().generate("Empty", [])

    assert result.row_count == 0
    assert "Total records: 0" in result.content
