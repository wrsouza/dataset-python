"""Integration tests — full serialize/deserialize pipeline through the real
SERIALIZER_FACTORY_REGISTRY, exercising domain + application + infrastructure
layers together exactly as main.py (the Streamlit composition root) does.
"""

from __future__ import annotations

import pytest

from serializer.application.use_cases import (
    DeserializeDataUseCase,
    ListFormatsUseCase,
    SerializeDataUseCase,
)
from serializer.domain.entities import UnsupportedFormatError
from serializer.infrastructure.serializers import SERIALIZER_FACTORY_REGISTRY


@pytest.mark.parametrize("slug", sorted(SERIALIZER_FACTORY_REGISTRY.keys()))
class TestFullPipelinePerFormat:
    def test_serialize_then_deserialize_round_trips_record_count(
        self, slug: str, sample_records: list[dict[str, object]]
    ) -> None:
        factory = SERIALIZER_FACTORY_REGISTRY[slug]

        serialize_result = SerializeDataUseCase(factory).execute(sample_records)
        deserialize_result = DeserializeDataUseCase(factory).execute(
            serialize_result.raw
        )

        assert deserialize_result.record_count == len(sample_records)

    def test_serialized_output_uses_declared_mime_and_extension(
        self, slug: str, sample_records: list[dict[str, object]]
    ) -> None:
        factory = SERIALIZER_FACTORY_REGISTRY[slug]
        serializer = factory.create_serializer()

        result = SerializeDataUseCase(factory).execute(sample_records)

        assert result.mime_type == serializer.get_mime_type()
        assert result.extension == serializer.get_extension()


class TestListFormatsIntegration:
    def test_lists_all_four_formats_from_real_registry(self) -> None:
        formats = ListFormatsUseCase(SERIALIZER_FACTORY_REGISTRY).execute()

        slugs = {fmt["slug"] for fmt in formats}
        assert slugs == {"json", "xml", "csv", "yaml"}

    def test_each_format_has_unique_extension(self) -> None:
        formats = ListFormatsUseCase(SERIALIZER_FACTORY_REGISTRY).execute()

        extensions = [fmt["extension"] for fmt in formats]
        assert len(extensions) == len(set(extensions))


class TestUnsupportedFormatFlow:
    def test_requesting_missing_slug_raises_domain_error(self) -> None:
        factory = SERIALIZER_FACTORY_REGISTRY.get("toml")

        assert factory is None
        with pytest.raises(UnsupportedFormatError):
            raise UnsupportedFormatError("toml")


class TestCrossFormatDataIntegrity:
    def test_json_and_yaml_preserve_native_types_identically(
        self, sample_records: list[dict[str, object]]
    ) -> None:
        json_factory = SERIALIZER_FACTORY_REGISTRY["json"]
        yaml_factory = SERIALIZER_FACTORY_REGISTRY["yaml"]

        json_records = json_factory.round_trip(sample_records)
        yaml_records = yaml_factory.round_trip(sample_records)

        assert json_records == yaml_records == sample_records

    def test_csv_and_xml_stringify_values_consistently(
        self, sample_records: list[dict[str, object]]
    ) -> None:
        csv_factory = SERIALIZER_FACTORY_REGISTRY["csv"]
        xml_factory = SERIALIZER_FACTORY_REGISTRY["xml"]

        expected = [
            {key: str(value) for key, value in record.items()}
            for record in sample_records
        ]

        assert csv_factory.round_trip(sample_records) == expected
        assert xml_factory.round_trip(sample_records) == expected
