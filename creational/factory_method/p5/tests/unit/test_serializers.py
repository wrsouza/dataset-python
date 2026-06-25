"""Unit tests for each ConcreteCreator/ConcreteProduct pair in infrastructure."""

from __future__ import annotations

import pytest

from serializer.domain.entities import DeserializationError, SerializationError
from serializer.domain.interfaces import SerializerFactory
from serializer.infrastructure.serializers import (
    SERIALIZER_FACTORY_REGISTRY,
    CSVSerializerFactory,
    JSONSerializerFactory,
    XMLSerializerFactory,
    YAMLSerializerFactory,
)

ALL_FACTORIES: list[SerializerFactory] = [
    JSONSerializerFactory(),
    XMLSerializerFactory(),
    CSVSerializerFactory(),
    YAMLSerializerFactory(),
]


class TestRegistry:
    def test_registry_has_one_entry_per_format(self) -> None:
        assert set(SERIALIZER_FACTORY_REGISTRY.keys()) == {
            "json",
            "xml",
            "csv",
            "yaml",
        }

    def test_registry_values_are_serializer_factories(self) -> None:
        for factory in SERIALIZER_FACTORY_REGISTRY.values():
            assert isinstance(factory, SerializerFactory)


@pytest.mark.parametrize("factory", ALL_FACTORIES, ids=lambda f: f.get_format_name())
class TestFactoryMethodContract:
    """Every ConcreteCreator must honor the same Creator contract (LSP)."""

    def test_create_serializer_returns_object_with_full_protocol(
        self, factory: SerializerFactory
    ) -> None:
        serializer = factory.create_serializer()

        assert hasattr(serializer, "serialize")
        assert hasattr(serializer, "deserialize")
        assert hasattr(serializer, "get_mime_type")
        assert hasattr(serializer, "get_extension")

    def test_round_trip_preserves_record_count(
        self, factory: SerializerFactory, sample_records: list[dict[str, object]]
    ) -> None:
        result = factory.round_trip(sample_records)

        assert len(result) == len(sample_records)

    def test_get_mime_type_is_non_empty(self, factory: SerializerFactory) -> None:
        serializer = factory.create_serializer()

        assert serializer.get_mime_type()

    def test_get_extension_is_lowercase_word(self, factory: SerializerFactory) -> None:
        serializer = factory.create_serializer()

        assert serializer.get_extension().isalpha()
        assert serializer.get_extension().islower()


class TestJSONSerializer:
    def test_serialize_produces_valid_utf8_json(
        self, sample_records: list[dict[str, object]]
    ) -> None:
        serializer = JSONSerializerFactory().create_serializer()

        raw = serializer.serialize(sample_records)

        assert b'"name": "Alice"' in raw

    def test_round_trip_preserves_values(
        self, sample_records: list[dict[str, object]]
    ) -> None:
        serializer = JSONSerializerFactory().create_serializer()

        raw = serializer.serialize(sample_records)
        result = serializer.deserialize(raw)

        assert result == sample_records

    def test_deserialize_rejects_non_array_top_level(self) -> None:
        serializer = JSONSerializerFactory().create_serializer()

        with pytest.raises(DeserializationError):
            serializer.deserialize(b'{"not": "a list"}')

    def test_deserialize_rejects_invalid_json(self) -> None:
        serializer = JSONSerializerFactory().create_serializer()

        with pytest.raises(DeserializationError):
            serializer.deserialize(b"{not valid json")

    def test_serialize_wraps_unserializable_objects(self) -> None:
        serializer = JSONSerializerFactory().create_serializer()

        with pytest.raises(SerializationError):
            serializer.serialize([{"bad": object()}])

    def test_get_mime_type_and_extension(self) -> None:
        factory = JSONSerializerFactory()
        serializer = factory.create_serializer()

        assert serializer.get_mime_type() == "application/json"
        assert serializer.get_extension() == "json"
        assert factory.get_format_name() == "JSON"


class TestXMLSerializer:
    def test_round_trip_preserves_values_as_strings(
        self, sample_records: list[dict[str, object]]
    ) -> None:
        serializer = XMLSerializerFactory().create_serializer()

        raw = serializer.serialize(sample_records)
        result = serializer.deserialize(raw)

        assert result == [
            {key: str(value) for key, value in record.items()}
            for record in sample_records
        ]

    def test_serialize_includes_xml_declaration(
        self, sample_records: list[dict[str, object]]
    ) -> None:
        serializer = XMLSerializerFactory().create_serializer()

        raw = serializer.serialize(sample_records)

        assert raw.startswith(b"<?xml")

    def test_deserialize_rejects_malformed_xml(self) -> None:
        serializer = XMLSerializerFactory().create_serializer()

        with pytest.raises(DeserializationError):
            serializer.deserialize(b"<records><record><unclosed></records>")

    def test_get_mime_type_and_extension(self) -> None:
        factory = XMLSerializerFactory()
        serializer = factory.create_serializer()

        assert serializer.get_mime_type() == "application/xml"
        assert serializer.get_extension() == "xml"
        assert factory.get_format_name() == "XML"


class TestCSVSerializer:
    def test_round_trip_preserves_values_as_strings(
        self, sample_records: list[dict[str, object]]
    ) -> None:
        serializer = CSVSerializerFactory().create_serializer()

        raw = serializer.serialize(sample_records)
        result = serializer.deserialize(raw)

        assert result == [
            {key: str(value) for key, value in record.items()}
            for record in sample_records
        ]

    def test_serialize_empty_list_returns_empty_bytes(self) -> None:
        serializer = CSVSerializerFactory().create_serializer()

        assert serializer.serialize([]) == b""

    def test_deserialize_empty_bytes_returns_empty_list(self) -> None:
        serializer = CSVSerializerFactory().create_serializer()

        assert serializer.deserialize(b"") == []

    def test_get_mime_type_and_extension(self) -> None:
        factory = CSVSerializerFactory()
        serializer = factory.create_serializer()

        assert serializer.get_mime_type() == "text/csv"
        assert serializer.get_extension() == "csv"
        assert factory.get_format_name() == "CSV"


class TestYAMLSerializer:
    def test_round_trip_preserves_values(
        self, sample_records: list[dict[str, object]]
    ) -> None:
        serializer = YAMLSerializerFactory().create_serializer()

        raw = serializer.serialize(sample_records)
        result = serializer.deserialize(raw)

        assert result == sample_records

    def test_deserialize_empty_document_returns_empty_list(self) -> None:
        serializer = YAMLSerializerFactory().create_serializer()

        assert serializer.deserialize(b"") == []

    def test_deserialize_rejects_non_sequence_top_level(self) -> None:
        serializer = YAMLSerializerFactory().create_serializer()

        with pytest.raises(DeserializationError):
            serializer.deserialize(b"key: value\n")

    def test_deserialize_rejects_invalid_yaml(self) -> None:
        serializer = YAMLSerializerFactory().create_serializer()

        with pytest.raises(DeserializationError):
            serializer.deserialize(b"- [unterminated\n  - flow")

    def test_get_mime_type_and_extension(self) -> None:
        factory = YAMLSerializerFactory()
        serializer = factory.create_serializer()

        assert serializer.get_mime_type() == "application/x-yaml"
        assert serializer.get_extension() == "yaml"
        assert factory.get_format_name() == "YAML"
