"""Domain entities for the data import pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class ImportStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class ValidationError:
    row_index: int
    field: str
    message: str


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    valid_records: list[dict[str, Any]] = field(default_factory=list)
    invalid_records: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def success(cls, records: list[dict[str, Any]]) -> ValidationResult:
        return cls(is_valid=True, valid_records=records)

    @classmethod
    def failure(
        cls,
        errors: list[ValidationError],
        invalid_records: list[dict[str, Any]],
    ) -> ValidationResult:
        return cls(is_valid=False, errors=errors, invalid_records=invalid_records)


@dataclass
class ImportReport:
    job_id: str
    format: str
    total_records: int
    persisted_count: int
    failed_count: int
    errors: list[ValidationError]
    duration_seconds: float
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ImportResult:
    job_id: str
    status: ImportStatus
    report: ImportReport | None = None
    error_message: str | None = None


class DataImportError(Exception):
    """Raised when the import pipeline encounters an unrecoverable error."""

    def __init__(self, job_id: str, reason: str) -> None:
        self.job_id = job_id
        self.reason = reason
        super().__init__(f"Import {job_id} failed: {reason}")


class ParseError(Exception):
    """Raised when raw bytes cannot be parsed into records."""

    def __init__(self, format_name: str, detail: str) -> None:
        self.format_name = format_name
        self.detail = detail
        super().__init__(f"Cannot parse {format_name}: {detail}")
