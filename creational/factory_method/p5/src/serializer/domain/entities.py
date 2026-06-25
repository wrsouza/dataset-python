"""Domain entities for the Serializer Factory pattern."""

from __future__ import annotations

from enum import StrEnum


class SerializationFormat(StrEnum):
    """Supported serialization formats."""

    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    CSV = "csv"


class SerializationError(Exception):
    """Raised when serialization fails."""


class DeserializationError(Exception):
    """Raised when deserialization fails or data is corrupt."""


class UnsupportedFormatError(Exception):
    """Raised when an unsupported format is requested."""

    def __init__(self, fmt: str) -> None:
        available = ", ".join(f.value for f in SerializationFormat)
        super().__init__(f"Format '{fmt}' is not supported. Available: {available}")
