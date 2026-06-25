"""Domain entities for the Report Builder."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ReportFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


@dataclass
class DataTable:
    headers: list[str]
    rows: list[list[str | int | float]]
    title: str = ""


@dataclass
class ChartSpec:
    """Specification for a chart (used by PDF/Excel builders)."""

    chart_type: str  # bar, line, pie
    title: str
    x_labels: list[str]
    y_values: list[float]


@dataclass
class Report:
    """Product: the fully built report, agnostic of output format."""

    title: str
    headers: list[str] = field(default_factory=list)
    data_tables: list[DataTable] = field(default_factory=list)
    charts: list[ChartSpec] = field(default_factory=list)
    footer: str = ""
    format: ReportFormat = ReportFormat.CSV

    # The rendered output bytes (set by the ConcreteBuilder on build())
    output: bytes = field(default_factory=bytes)
    content_type: str = "application/octet-stream"
    filename: str = "report"
