"""Unit tests for XmlFormatExporter."""

from __future__ import annotations

from xml.etree.ElementTree import fromstring

from exporter.domain.entities import Report
from exporter.infrastructure.xml_exporter import XmlFormatExporter


def test_serialize_produces_well_formed_xml(sample_report: Report) -> None:
    exporter = XmlFormatExporter()

    root = fromstring(exporter.serialize(sample_report))

    assert root.tag == "report"
    assert root.attrib["title"] == "Sales Report"
    rows = root.find("rows")
    assert rows is not None
    assert len(rows.findall("row")) == 2


def test_serialize_handles_none_values() -> None:
    from exporter.domain.entities import ReportColumn, ReportRow

    report = Report(
        title="Nulls",
        columns=[ReportColumn(name="x", label="X")],
        rows=[ReportRow(values={"x": None})],
    )
    exporter = XmlFormatExporter()

    root = fromstring(exporter.serialize(report))

    field = root.find("rows/row/x")
    assert field is not None
    assert field.text in (None, "")


def test_format_metadata() -> None:
    exporter = XmlFormatExporter()

    assert exporter.file_extension() == "xml"
    assert exporter.format_name() == "XML"
