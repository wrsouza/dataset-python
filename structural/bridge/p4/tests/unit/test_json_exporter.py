"""Unit tests for JsonFormatExporter."""

from __future__ import annotations

import json

from exporter.domain.entities import Report
from exporter.infrastructure.json_exporter import JsonFormatExporter


def test_serialize_produces_valid_json_structure(sample_report: Report) -> None:
    exporter = JsonFormatExporter()

    payload = json.loads(exporter.serialize(sample_report).decode("utf-8"))

    assert payload["title"] == "Sales Report"
    assert payload["columns"] == ["product", "units"]
    assert payload["rows"][0]["product"] == "Widget"


def test_format_metadata() -> None:
    exporter = JsonFormatExporter()

    assert exporter.file_extension() == "json"
    assert exporter.format_name() == "JSON"
