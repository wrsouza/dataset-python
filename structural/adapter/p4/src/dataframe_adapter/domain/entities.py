"""Domain entities and exceptions for dataframe_adapter.

Pure Python dataclasses — no pandas, no Streamlit, no parser dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ParsedDataset:
    """Value object representing tabular data in a format-agnostic shape.

    Every concrete Adapter (CSV, JSON, Parquet) must translate its source
    format into this single representation, so the rest of the application
    never needs to know which parser produced the data.
    """

    columns: list[str]
    rows: list[list[str]]
    source_format: str
    row_count: int = field(init=False)

    def __post_init__(self) -> None:
        self.row_count = len(self.rows)

    def to_csv_text(self) -> str:
        """Serialize this dataset as a normalized CSV string (header + rows)."""
        lines = [",".join(_escape_csv_field(value) for value in self.columns)]
        for row in self.rows:
            lines.append(",".join(_escape_csv_field(value) for value in row))
        return "\n".join(lines) + "\n"


def _escape_csv_field(value: str) -> str:
    """Quote *value* if it contains a comma, quote or newline (RFC 4180-lite)."""
    if any(symbol in value for symbol in (",", '"', "\n")):
        return '"' + value.replace('"', '""') + '"'
    return value


# ── Domain exceptions ───────────────────────────────────────────────────────


class DataframeAdapterError(Exception):
    """Base class for all dataframe_adapter domain errors."""


class UnsupportedFormatError(DataframeAdapterError):
    """Raised when no registered Adapter can handle the given file format."""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        super().__init__(f"Formato não suportado para o arquivo: {filename}")


class InvalidDataError(DataframeAdapterError):
    """Raised when the file content cannot be parsed as valid tabular data."""

    def __init__(self, source_format: str, reason: str) -> None:
        self.source_format = source_format
        self.reason = reason
        super().__init__(f"Dados inválidos para formato '{source_format}': {reason}")
