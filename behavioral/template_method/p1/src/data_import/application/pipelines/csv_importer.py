"""CSVImporter — ConcreteClass for CSV data sources."""

from __future__ import annotations

import csv
import io
from typing import Any

from data_import.domain.entities import ValidationError, ValidationResult
from data_import.domain.interfaces import DataImporter


class CSVImporter(DataImporter):
    """Imports data from comma-separated value files."""

    REQUIRED_FIELDS = {"id", "name", "value"}

    def read_raw(self, path: str) -> bytes:
        with open(path, "rb") as fh:
            return fh.read()

    def parse(self, raw: bytes) -> list[dict[str, Any]]:
        text = raw.decode("utf-8-sig")  # handle BOM
        reader = csv.DictReader(io.StringIO(text))
        return [dict(row) for row in reader]

    def validate(self, records: list[dict[str, Any]]) -> ValidationResult:
        errors: list[ValidationError] = []
        invalid: list[dict[str, Any]] = []
        valid: list[dict[str, Any]] = []

        for idx, record in enumerate(records):
            row_errors = self._validate_record(idx, record)
            if row_errors:
                errors.extend(row_errors)
                invalid.append(record)
            else:
                valid.append(record)

        if errors:
            return ValidationResult(
                is_valid=False,
                errors=errors,
                valid_records=valid,
                invalid_records=invalid,
            )
        return ValidationResult.success(valid)

    def transform(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "external_id": str(r.get("id", "")).strip(),
                "name": str(r.get("name", "")).strip(),
                "value": self._parse_float(r.get("value")),
                "source_format": "CSV",
            }
            for r in records
        ]

    # ── Hook override ────────────────────────────────────────────────────────────

    def on_validation_error(self, errors: list[ValidationError]) -> bool:
        # CSV imports tolerate partial failures — continue with valid rows.
        return True

    # ── Private helpers ──────────────────────────────────────────────────────────

    def _validate_record(
        self, idx: int, record: dict[str, Any]
    ) -> list[ValidationError]:
        errs: list[ValidationError] = []
        for field in self.REQUIRED_FIELDS:
            if not record.get(field):
                errs.append(ValidationError(idx, field, f"Field '{field}' is required"))
        return errs

    @staticmethod
    def _parse_float(value: str | float | None) -> float:
        try:
            return float(str(value).replace(",", "."))
        except (ValueError, TypeError):
            return 0.0
