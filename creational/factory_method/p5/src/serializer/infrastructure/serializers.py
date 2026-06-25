"""ConcreteCreators and ConcreteProducts for each serialization format.

Each ConcreteCreator overrides create_serializer() to return its specific
ConcreteProduct. Adding a new format (e.g. MessagePack) = add one
new pair here. Zero changes to SerializerFactory ABC (OCP).

All implementations use stdlib where possible; third-party only for
YAML (PyYAML).
"""

from __future__ import annotations

import csv
import io
import json
import xml.etree.ElementTree as ET
from typing import Any

from serializer.domain.entities import DeserializationError, SerializationError
from serializer.domain.interfaces import DataSerializer, SerializerFactory

# ── JSON ──────────────────────────────────────────────────────────────────────


class JSONSerializer:
    """ConcreteProduct — serialize/deserialize using the stdlib json module."""

    def serialize(self, data: list[dict[str, Any]]) -> bytes:
        try:
            return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise SerializationError(f"JSON serialization failed: {exc}") from exc

    def deserialize(self, data: bytes) -> list[dict[str, Any]]:
        try:
            result = json.loads(data.decode("utf-8"))
            if not isinstance(result, list):
                raise DeserializationError("Expected a JSON array at the top level.")
            return result
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DeserializationError(f"JSON deserialization failed: {exc}") from exc

    def get_mime_type(self) -> str:
        return "application/json"

    def get_extension(self) -> str:
        return "json"


class JSONSerializerFactory(SerializerFactory):
    """ConcreteCreator — creates a JSONSerializer."""

    def create_serializer(self) -> DataSerializer:
        return JSONSerializer()

    def get_format_name(self) -> str:
        return "JSON"


# ── XML ───────────────────────────────────────────────────────────────────────


class XMLSerializer:
    """ConcreteProduct — serialize/deserialize using stdlib xml.etree.ElementTree."""

    _ROOT_TAG = "records"
    _ITEM_TAG = "record"

    def serialize(self, data: list[dict[str, Any]]) -> bytes:
        try:
            root = ET.Element(self._ROOT_TAG)
            for row in data:
                item = ET.SubElement(root, self._ITEM_TAG)
                for key, value in row.items():
                    child = ET.SubElement(item, str(key))
                    child.text = str(value) if value is not None else ""
            tree = ET.ElementTree(root)
            buf = io.BytesIO()
            tree.write(buf, encoding="utf-8", xml_declaration=True)
            return buf.getvalue()
        except Exception as exc:
            raise SerializationError(f"XML serialization failed: {exc}") from exc

    def deserialize(self, data: bytes) -> list[dict[str, Any]]:
        try:
            root = ET.fromstring(data.decode("utf-8"))  # noqa: S314
            records: list[dict[str, Any]] = []
            for item in root.findall(self._ITEM_TAG):
                record: dict[str, Any] = {}
                for child in item:
                    record[child.tag] = child.text or ""
                records.append(record)
            return records
        except ET.ParseError as exc:
            raise DeserializationError(f"XML deserialization failed: {exc}") from exc

    def get_mime_type(self) -> str:
        return "application/xml"

    def get_extension(self) -> str:
        return "xml"


class XMLSerializerFactory(SerializerFactory):
    """ConcreteCreator — creates a XMLSerializer."""

    def create_serializer(self) -> DataSerializer:
        return XMLSerializer()

    def get_format_name(self) -> str:
        return "XML"


# ── CSV ───────────────────────────────────────────────────────────────────────


class CSVSerializer:
    """ConcreteProduct — serialize/deserialize using the stdlib csv module."""

    def serialize(self, data: list[dict[str, Any]]) -> bytes:
        if not data:
            return b""
        try:
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=list(data[0].keys()))
            writer.writeheader()
            writer.writerows(data)
            return buf.getvalue().encode("utf-8")
        except Exception as exc:
            raise SerializationError(f"CSV serialization failed: {exc}") from exc

    def deserialize(self, data: bytes) -> list[dict[str, Any]]:
        try:
            buf = io.StringIO(data.decode("utf-8"))
            reader = csv.DictReader(buf)
            return [dict(row) for row in reader]
        except Exception as exc:
            raise DeserializationError(f"CSV deserialization failed: {exc}") from exc

    def get_mime_type(self) -> str:
        return "text/csv"

    def get_extension(self) -> str:
        return "csv"


class CSVSerializerFactory(SerializerFactory):
    """ConcreteCreator — creates a CSVSerializer."""

    def create_serializer(self) -> DataSerializer:
        return CSVSerializer()

    def get_format_name(self) -> str:
        return "CSV"


# ── YAML ──────────────────────────────────────────────────────────────────────


class YAMLSerializer:
    """ConcreteProduct — serialize/deserialize using PyYAML.

    DIP: business logic never imports yaml; only this infrastructure
    class does. If PyYAML is unavailable the error is domain-typed.
    """

    def serialize(self, data: list[dict[str, Any]]) -> bytes:
        try:
            import yaml

            return yaml.safe_dump(data, allow_unicode=True, sort_keys=False).encode(
                "utf-8"
            )
        except ImportError as exc:
            raise SerializationError(
                "PyYAML is required for YAML serialization. "
                "Install it with: pip install pyyaml"
            ) from exc
        except yaml.YAMLError as exc:
            raise SerializationError(f"YAML serialization failed: {exc}") from exc

    def deserialize(self, data: bytes) -> list[dict[str, Any]]:
        try:
            import yaml

            result = yaml.safe_load(data.decode("utf-8"))
            if result is None:
                return []
            if not isinstance(result, list):
                raise DeserializationError("Expected a YAML sequence at the top level.")
            return result
        except ImportError as exc:
            raise DeserializationError(
                "PyYAML is required for YAML deserialization."
            ) from exc
        except (UnicodeDecodeError, yaml.YAMLError) as exc:
            raise DeserializationError(f"YAML deserialization failed: {exc}") from exc

    def get_mime_type(self) -> str:
        return "application/x-yaml"

    def get_extension(self) -> str:
        return "yaml"


class YAMLSerializerFactory(SerializerFactory):
    """ConcreteCreator — creates a YAMLSerializer."""

    def create_serializer(self) -> DataSerializer:
        return YAMLSerializer()

    def get_format_name(self) -> str:
        return "YAML"


# ── Registry ──────────────────────────────────────────────────────────────────

SERIALIZER_FACTORY_REGISTRY: dict[str, SerializerFactory] = {
    "json": JSONSerializerFactory(),
    "xml": XMLSerializerFactory(),
    "csv": CSVSerializerFactory(),
    "yaml": YAMLSerializerFactory(),
}
