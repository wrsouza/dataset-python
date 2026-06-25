"""JSONImporter — ConcreteClass for JSON data sources."""

from __future__ import annotations

import json
from typing import Any

from data_import.domain.entities import ValidationError, ValidationResult
from data_import.domain.interfaces import DataImporter, ParseError


class JSONImporter(DataImporter):
    """Imports data from JSON files (array of objects at root)."""

    REQUIRED_FIELDS = {"id", "name", "value"}

    def read_raw(self, path: str) -> bytes:
        with open(path, "rb") as fh:
            return fh.read()

    def parse(self, raw: bytes) -> list[dict[str, Any]]:
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ParseError("JSON", str(exc)) from exc

        if isinstance(data, list):
            return list(data)
        if isinstance(data, dict) and "records" in data:
            return list(data["records"])
        raise ParseError(
            "JSON", "Root must be an array or an object with 'records' key"
        )

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
                "external_id": str(r.get("id", "")),
                "name": str(r.get("name", "")).strip(),
                "value": float(r.get("value", 0)),
                "source_format": "JSON",
                "metadata": {
                    k: v for k, v in r.items() if k not in self.REQUIRED_FIELDS
                },
            }
            for r in records
        ]

    # JSON imports are strict — default hook (abort on error) is kept.

    def _validate_record(
        self, idx: int, record: dict[str, Any]
    ) -> list[ValidationError]:
        errs: list[ValidationError] = []
        for field in self.REQUIRED_FIELDS:
            if record.get(field) is None:
                errs.append(ValidationError(idx, field, f"Field '{field}' is required"))
        return errs
