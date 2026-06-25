"""AbstractClass for the Template Method pattern — DataImporter.

Template Method defines the skeleton of the import algorithm in import_data().
Subclasses override read_raw() and parse() without changing the overall flow.
"""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from typing import Any

from data_import.domain.entities import (
    ImportReport,
    ImportResult,
    ImportStatus,
    ParseError,
    ValidationError,
    ValidationResult,
)

__all__ = ["DataImporter", "ParseError"]


class DataImporter(ABC):
    """AbstractClass: defines the import_data template method.

    Fixed steps (always run in this order):
        1. read_raw   — abstract, subclass-specific
        2. parse      — abstract, subclass-specific
        3. validate   — abstract, subclass-specific
        4. transform  — abstract, subclass-specific
        5. persist    — concrete, shared PostgreSQL logic
        6. generate_report — concrete, shared reporting logic

    Hook:
        on_validation_error() — returns True to continue with valid records,
                                False (default) to abort the import.
    """

    @abstractmethod
    def read_raw(self, path: str) -> bytes:
        """Read bytes from the source path."""

    @abstractmethod
    def parse(self, raw: bytes) -> list[dict[str, Any]]:
        """Parse raw bytes into a list of record dicts."""

    @abstractmethod
    def validate(self, records: list[dict[str, Any]]) -> ValidationResult:
        """Validate parsed records; return ValidationResult with errors."""

    @abstractmethod
    def transform(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transform and normalise records before persistence."""

    # ── Hook ────────────────────────────────────────────────────────────────────

    def on_validation_error(self, errors: list[ValidationError]) -> bool:
        """Called when validation finds errors.

        Returns:
            True  → continue import with valid records only.
            False → abort (default).
        """
        return False

    # ── Concrete steps ──────────────────────────────────────────────────────────

    def persist(self, records: list[dict[str, Any]]) -> int:
        """Persist records to PostgreSQL; returns count of rows inserted."""
        from data_import.infrastructure.postgres_repository import (
            PostgresImportRepository,
        )

        repo = PostgresImportRepository()
        return repo.bulk_insert(records)

    def generate_report(
        self,
        job_id: str,
        format_name: str,
        total: int,
        persisted: int,
        errors: list[ValidationError],
        duration: float,
    ) -> ImportReport:
        return ImportReport(
            job_id=job_id,
            format=format_name,
            total_records=total,
            persisted_count=persisted,
            failed_count=total - persisted,
            errors=errors,
            duration_seconds=duration,
        )

    # ── Template Method ─────────────────────────────────────────────────────────

    def import_data(self, source_path: str) -> ImportResult:
        """Template method — defines the fixed import algorithm."""
        job_id = str(uuid.uuid4())
        start = time.monotonic()
        errors: list[ValidationError] = []
        persisted = 0
        total = 0

        try:
            raw = self.read_raw(source_path)
            records = self.parse(raw)
            total = len(records)

            validation = self.validate(records)

            if not validation.is_valid:
                errors = validation.errors
                should_continue = self.on_validation_error(errors)
                if not should_continue:
                    duration = time.monotonic() - start
                    report = self.generate_report(
                        job_id, self._format_name(), total, 0, errors, duration
                    )
                    return ImportResult(
                        job_id=job_id,
                        status=ImportStatus.FAILED,
                        report=report,
                    )
                # Continue with only the valid subset
                records = validation.valid_records

            transformed = self.transform(records)
            persisted = self.persist(transformed)

            duration = time.monotonic() - start
            status = ImportStatus.PARTIAL if errors else ImportStatus.COMPLETED
            report = self.generate_report(
                job_id, self._format_name(), total, persisted, errors, duration
            )
            return ImportResult(job_id=job_id, status=status, report=report)

        except Exception as exc:
            duration = time.monotonic() - start
            report = self.generate_report(
                job_id, self._format_name(), total, persisted, errors, duration
            )
            return ImportResult(
                job_id=job_id,
                status=ImportStatus.FAILED,
                report=report,
                error_message=str(exc),
            )

    def _format_name(self) -> str:
        """Derive format name from concrete class name for reports."""
        return type(self).__name__.replace("Importer", "").upper()
