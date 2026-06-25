"""Application use cases for the Serializer Factory.

Use cases depend on SerializerFactory (abstraction), never on concrete
JSON/XML/Parquet/CSV classes (DIP). Each use case has one responsibility (SRP).
"""

from __future__ import annotations

from dataclasses import dataclass

from serializer.domain.interfaces import SerializerFactory


@dataclass(frozen=True)
class SerializeResult:
    """Value object wrapping the result of a serialize operation."""

    raw: bytes
    mime_type: str
    extension: str
    record_count: int

    @property
    def size_bytes(self) -> int:
        return len(self.raw)

    @property
    def size_kb(self) -> float:
        return round(self.size_bytes / 1024, 2)


@dataclass(frozen=True)
class DeserializeResult:
    """Value object wrapping the result of a deserialize operation."""

    records: list[dict[str, object]]
    record_count: int


class SerializeDataUseCase:
    """Serialize a list of records using any SerializerFactory.

    SRP: this class only knows how to orchestrate serialization.
    DIP: receives SerializerFactory via constructor.
    """

    def __init__(self, factory: SerializerFactory) -> None:
        self._factory = factory

    def execute(self, data: list[dict[str, object]]) -> SerializeResult:
        """Run serialization and return a structured result.

        Args:
            data: list of records to serialize.

        Returns:
            SerializeResult with bytes, MIME type, extension, and metadata.
        """
        serializer = self._factory.create_serializer()
        raw = serializer.serialize(data)
        return SerializeResult(
            raw=raw,
            mime_type=serializer.get_mime_type(),
            extension=serializer.get_extension(),
            record_count=len(data),
        )


class DeserializeDataUseCase:
    """Deserialize bytes into records using any SerializerFactory.

    SRP: this class only knows how to orchestrate deserialization.
    DIP: receives SerializerFactory via constructor.
    """

    def __init__(self, factory: SerializerFactory) -> None:
        self._factory = factory

    def execute(self, raw: bytes) -> DeserializeResult:
        """Run deserialization and return a structured result.

        Args:
            raw: bytes to deserialize.

        Returns:
            DeserializeResult with records and record count.
        """
        serializer = self._factory.create_serializer()
        records = serializer.deserialize(raw)
        return DeserializeResult(records=records, record_count=len(records))


class ListFormatsUseCase:
    """Return metadata about all registered serialization formats."""

    def __init__(self, registry: dict[str, SerializerFactory]) -> None:
        self._registry = registry

    def execute(self) -> list[dict[str, str]]:
        """Return format names, slugs, MIME types, and extensions."""
        result = []
        for slug, factory in self._registry.items():
            serializer = factory.create_serializer()
            result.append(
                {
                    "slug": slug,
                    "name": factory.get_format_name(),
                    "mime_type": serializer.get_mime_type(),
                    "extension": serializer.get_extension(),
                }
            )
        return result
