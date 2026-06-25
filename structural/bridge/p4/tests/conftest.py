"""Shared pytest fixtures for the Export Format Bridge test suite."""

from __future__ import annotations

import pytest

from exporter.domain.entities import Report, ReportColumn, ReportRow


@pytest.fixture
def sample_report() -> Report:
    """A small two-row report used across unit and integration tests."""
    columns = [
        ReportColumn(name="product", label="Product"),
        ReportColumn(name="units", label="Units"),
    ]
    rows = [
        ReportRow(values={"product": "Widget", "units": 10}),
        ReportRow(values={"product": "Gadget", "units": 5}),
    ]
    return Report(title="Sales Report", columns=columns, rows=rows)
