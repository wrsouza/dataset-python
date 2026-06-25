"""Unit tests for application/use_cases.py — DIP via factory injection."""

from __future__ import annotations

from typing import Any

from serializer.application.use_cases import (
    DeserializeDataUseCase,
    ListFormatsUseCase,
    SerializeDataUseCase,
)
from serializer.domain.interfaces import DataSerializer, SerializerFactory


class StubSerializer:
    def serialize(self, data: list[dict[str, Any]]) -> bytes:
        return b"stub-payload"

    def deserialize(self, data: bytes) -> list[dict[str, Any]]:
        return [{"stub": True}]

    def get_mime_type(self) -> str:
        return "application/x-stub"

    def get_extension(self) -> str:
        return "stub"


class StubSerializerFactory(SerializerFactory):
    def create_serializer(self) -> DataSerializer:
        return StubSerializer()  # type: ignore[return-value]

    def get_format_name(self) -> str:
        return "Stub"


class TestSerializeDataUseCase:
    def test_execute_returns_result_with_metadata(
        self, sample_records: list[dict[str, object]]
    ) -> None:
        use_case = SerializeDataUseCase(StubSerializerFactory())

        result = use_case.execute(sample_records)

        assert result.raw == b"stub-payload"
        assert result.mime_type == "application/x-stub"
        assert result.extension == "stub"
        assert result.record_count == len(sample_records)

    def test_size_kb_matches_raw_length(self) -> None:
        use_case = SerializeDataUseCase(StubSerializerFactory())

        result = use_case.execute([])

        assert result.size_bytes == len(b"stub-payload")
        assert result.size_kb == round(len(b"stub-payload") / 1024, 2)


class TestDeserializeDataUseCase:
    def test_execute_returns_records_and_count(self) -> None:
        use_case = DeserializeDataUseCase(StubSerializerFactory())

        result = use_case.execute(b"irrelevant")

        assert result.records == [{"stub": True}]
        assert result.record_count == 1


class TestListFormatsUseCase:
    def test_execute_returns_metadata_for_each_registered_factory(self) -> None:
        registry = {"stub": StubSerializerFactory()}
        use_case = ListFormatsUseCase(registry)

        result = use_case.execute()

        assert result == [
            {
                "slug": "stub",
                "name": "Stub",
                "mime_type": "application/x-stub",
                "extension": "stub",
            }
        ]

    def test_execute_returns_empty_list_for_empty_registry(self) -> None:
        use_case = ListFormatsUseCase({})

        assert use_case.execute() == []
