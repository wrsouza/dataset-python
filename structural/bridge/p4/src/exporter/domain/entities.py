"""Domain entities for the Export Format Bridge.

These are plain data structures with no knowledge of how they will be
serialized — serialization format is the Implementor side of the Bridge.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ReportColumn:
    """A single named column used to keep row dicts ordered and typed."""

    name: str
    label: str


@dataclass(frozen=True)
class ReportRow:
    """One row of report data, keyed by column name."""

    values: dict[str, str | int | float | bool | None]


@dataclass(frozen=True)
class Report:
    """A tabular report: a title, ordered columns, and a list of rows."""

    title: str
    columns: list[ReportColumn]
    rows: list[ReportRow] = field(default_factory=list)

    def column_names(self) -> list[str]:
        """Return column names in declaration order."""
        return [column.name for column in self.columns]


@dataclass(frozen=True)
class ExportResult:
    """Outcome of an export operation: where the data landed and its size."""

    destination: str
    format_name: str
    byte_size: int

    def to_dict(self) -> dict[str, str | int]:
        """Serialize the result for CLI/JSON-friendly display."""
        return {
            "destination": self.destination,
            "format_name": self.format_name,
            "byte_size": self.byte_size,
        }
