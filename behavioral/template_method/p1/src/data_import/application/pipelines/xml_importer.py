"""XMLImporter — ConcreteClass for XML data sources."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

from data_import.domain.entities import ValidationError, ValidationResult
from data_import.domain.interfaces import DataImporter, ParseError


class XMLImporter(DataImporter):
    """Imports data from XML files.

    Expected structure:
        <records>
            <record>
                <id>1</id>
                <name>foo</name>
                <value>42.0</value>
            </record>
        </records>
    """

    def read_raw(self, path: str) -> bytes:
        with open(path, "rb") as fh:
            return fh.read()

    def parse(self, raw: bytes) -> list[dict[str, Any]]:
        try:
            # Tutorial scope: input is an authenticated upload, not arbitrary
            # untrusted XML from the internet. A production system should
            # use defusedxml.ElementTree instead of stdlib ElementTree.
            root = ET.fromstring(raw.decode("utf-8"))  # noqa: S314
        except ET.ParseError as exc:
            raise ParseError("XML", str(exc)) from exc

        records: list[dict[str, Any]] = []
        tag = "record"
        for element in root.findall(tag):
            record: dict[str, Any] = {child.tag: child.text for child in element}
            records.append(record)
        return records

    def validate(self, records: list[dict[str, Any]]) -> ValidationResult:
        errors: list[ValidationError] = []
        invalid: list[dict[str, Any]] = []
        valid: list[dict[str, Any]] = []

        for idx, record in enumerate(records):
            row_errors: list[ValidationError] = []
            for field in ("id", "name", "value"):
                if not record.get(field):
                    row_errors.append(
                        ValidationError(idx, field, f"Element <{field}> is required")
                    )
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
                "value": self._safe_float(r.get("value")),
                "source_format": "XML",
            }
            for r in records
        ]

    # Hook: XML imports also tolerate partial failures
    def on_validation_error(self, errors: list[ValidationError]) -> bool:
        return True

    @staticmethod
    def _safe_float(value: str | float | None) -> float:
        try:
            return float(str(value))
        except (ValueError, TypeError):
            return 0.0
