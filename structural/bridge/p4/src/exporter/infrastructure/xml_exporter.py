"""XML concrete implementor for the Export Format Bridge."""

from __future__ import annotations

from xml.etree.ElementTree import Element, SubElement, tostring

from exporter.domain.entities import Report
from exporter.domain.interfaces import FormatExporter


class XmlFormatExporter(FormatExporter):
    """Encodes a Report as XML using the stdlib ElementTree builder."""

    def serialize(self, report: Report) -> bytes:
        root = Element("report", attrib={"title": report.title})
        rows_element = SubElement(root, "rows")
        for row in report.rows:
            self._append_row(rows_element, row.values)
        payload: bytes = tostring(root, encoding="utf-8", xml_declaration=True)
        return payload

    def _append_row(
        self, rows_element: Element, values: dict[str, str | int | float | bool | None]
    ) -> None:
        row_element = SubElement(rows_element, "row")
        for column_name, value in values.items():
            field_element = SubElement(row_element, column_name)
            field_element.text = "" if value is None else str(value)

    def file_extension(self) -> str:
        return "xml"

    def format_name(self) -> str:
        return "XML"
