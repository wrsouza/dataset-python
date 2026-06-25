"""Unit tests: verify steps are called in correct order and hooks work."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest

from data_import.domain.entities import (
    ImportStatus,
    ValidationError,
    ValidationResult,
)
from data_import.domain.interfaces import DataImporter


class ConcreteImporter(DataImporter):
    """Minimal concrete importer for testing."""

    def __init__(self) -> None:
        self.call_log: list[str] = []

    def read_raw(self, path: str) -> bytes:
        self.call_log.append("read_raw")
        return b"raw"

    def parse(self, raw: bytes) -> list[dict[str, Any]]:
        self.call_log.append("parse")
        return [{"id": "1", "name": "test", "value": 1.0}]

    def validate(self, records: list[dict[str, Any]]) -> ValidationResult:
        self.call_log.append("validate")
        return ValidationResult.success(records)

    def transform(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.call_log.append("transform")
        return records


class FailingValidationImporter(ConcreteImporter):
    """Importer where validation always fails."""

    def validate(self, records: list[dict[str, Any]]) -> ValidationResult:
        self.call_log.append("validate")
        errors = [ValidationError(0, "id", "missing")]
        return ValidationResult.failure(errors, records)


class PermissiveImporter(FailingValidationImporter):
    """Overrides hook to continue despite validation errors."""

    def on_validation_error(self, errors: list[ValidationError]) -> bool:
        self.call_log.append("on_validation_error")
        return True  # continue


@pytest.fixture
def patched_persist(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock(return_value=1)
    monkeypatch.setattr(DataImporter, "persist", mock)
    return mock


class TestStepOrder:
    def test_happy_path_calls_all_steps_in_order(
        self, patched_persist: MagicMock
    ) -> None:
        importer = ConcreteImporter()
        result = importer.import_data("/fake/path")

        assert importer.call_log == ["read_raw", "parse", "validate", "transform"]
        assert result.status == ImportStatus.COMPLETED

    def test_persist_called_after_transform(self, patched_persist: MagicMock) -> None:
        importer = ConcreteImporter()
        importer.import_data("/fake/path")

        patched_persist.assert_called_once()

    def test_validation_failure_aborts_without_persist(
        self, patched_persist: MagicMock
    ) -> None:
        importer = FailingValidationImporter()
        result = importer.import_data("/fake/path")

        assert result.status == ImportStatus.FAILED
        patched_persist.assert_not_called()

    def test_hook_continue_allows_partial_import(
        self, patched_persist: MagicMock
    ) -> None:
        importer = PermissiveImporter()
        result = importer.import_data("/fake/path")

        assert "on_validation_error" in importer.call_log
        # persist IS called when hook returns True
        patched_persist.assert_called_once()
        assert result.status in (ImportStatus.PARTIAL, ImportStatus.COMPLETED)


class TestCSVImporter:
    def test_parse_csv_bytes(self) -> None:
        from data_import.application.pipelines.csv_importer import CSVImporter

        importer = CSVImporter()
        raw = b"id,name,value\n1,Alice,42.5\n2,Bob,10.0"
        records = importer.parse(raw)
        assert len(records) == 2
        assert records[0]["name"] == "Alice"

    def test_transform_normalises_fields(self) -> None:
        from data_import.application.pipelines.csv_importer import CSVImporter

        importer = CSVImporter()
        records = [{"id": "1", "name": " Alice ", "value": "42,5"}]
        transformed = importer.transform(records)
        assert transformed[0]["source_format"] == "CSV"
        assert transformed[0]["name"] == "Alice"
        assert transformed[0]["value"] == pytest.approx(42.5)

    def test_on_validation_error_returns_true(self) -> None:
        from data_import.application.pipelines.csv_importer import CSVImporter

        importer = CSVImporter()
        assert importer.on_validation_error([]) is True


class TestJSONImporter:
    def test_parse_list_root(self) -> None:
        import json

        from data_import.application.pipelines.json_importer import JSONImporter

        importer = JSONImporter()
        data = [{"id": "1", "name": "A", "value": 1}]
        records = importer.parse(json.dumps(data).encode())
        assert records == data

    def test_parse_records_key(self) -> None:
        import json

        from data_import.application.pipelines.json_importer import JSONImporter

        importer = JSONImporter()
        data = {"records": [{"id": "2", "name": "B", "value": 2}]}
        records = importer.parse(json.dumps(data).encode())
        assert len(records) == 1

    def test_parse_invalid_json_raises(self) -> None:
        from data_import.application.pipelines.json_importer import JSONImporter
        from data_import.domain.interfaces import ParseError

        importer = JSONImporter()
        with pytest.raises(ParseError):
            importer.parse(b"not json")


class TestXMLImporter:
    def test_parse_xml_records(self) -> None:
        from data_import.application.pipelines.xml_importer import XMLImporter

        importer = XMLImporter()
        xml = (
            b"<records><record><id>1</id><name>A</name>"
            b"<value>5.0</value></record></records>"
        )
        records = importer.parse(xml)
        assert len(records) == 1
        assert records[0]["name"] == "A"

    def test_transform_source_format(self) -> None:
        from data_import.application.pipelines.xml_importer import XMLImporter

        importer = XMLImporter()
        records = [{"id": "1", "name": "A", "value": "5.0"}]
        result = importer.transform(records)
        assert result[0]["source_format"] == "XML"
