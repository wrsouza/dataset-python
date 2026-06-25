"""Unit tests for the SerializerFactory Creator ABC (domain/interfaces.py)."""

from __future__ import annotations

from typing import Any

import pytest

from serializer.domain.interfaces import DataSerializer, SerializerFactory


class FakeSerializer:
    """Minimal DataSerializer fake used to exercise the Creator's template method."""

    def __init__(self) -> None:
        self.serialized_with: list[dict[str, Any]] | None = None

    def serialize(self, data: list[dict[str, Any]]) -> bytes:
        self.serialized_with = data
        return b"fake-bytes"

    def deserialize(self, data: bytes) -> list[dict[str, Any]]:
        assert data == b"fake-bytes"
        return [{"echo": True}]

    def get_mime_type(self) -> str:
        return "application/x-fake"

    def get_extension(self) -> str:
        return "fake"


class FakeSerializerFactory(SerializerFactory):
    """ConcreteCreator used only in tests to validate the abstract base."""

    def create_serializer(self) -> DataSerializer:
        return FakeSerializer()  # type: ignore[return-value]


class TestSerializerFactory:
    def test_cannot_instantiate_abstract_factory(self) -> None:
        with pytest.raises(TypeError):
            SerializerFactory()  # type: ignore[abstract]

    def test_get_format_name_strips_suffix_by_default(self) -> None:
        factory = FakeSerializerFactory()

        assert factory.get_format_name() == "Fake"

    def test_round_trip_serializes_then_deserializes(
        self, sample_records: list[dict[str, object]]
    ) -> None:
        factory = FakeSerializerFactory()

        result = factory.round_trip(sample_records)

        assert result == [{"echo": True}]

    def test_round_trip_calls_factory_method(
        self, sample_records: list[dict[str, object]]
    ) -> None:
        factory = FakeSerializerFactory()
        serializer = factory.create_serializer()

        serializer.serialize(sample_records)

        assert serializer.serialized_with == sample_records  # type: ignore[union-attr]
