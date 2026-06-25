"""Domain interfaces for the Serializer Factory pattern.

Defines the Creator ABC and Product Protocol following Factory Method.
ISP: DataSerializer has the minimum viable interface — serialize,
deserialize, get_mime_type, get_extension.
DIP: high-level code depends on these abstractions, never on concrete
JSON/XML/Parquet/CSV implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class DataSerializer(Protocol):
    """Product interface — every concrete serializer must satisfy this contract.

    ISP: only 4 focused methods. Clients that only serialize never call
    deserialize (they can ignore it without violating the contract).
    """

    def serialize(self, data: list[dict[str, object]]) -> bytes:
        """Convert a list of records to bytes in the specific format.

        Args:
            data: list of dicts, each dict is a row/record.

        Returns:
            Serialized bytes representation.

        Raises:
            SerializationError: if the data cannot be converted.
        """
        ...

    def deserialize(self, data: bytes) -> list[dict[str, object]]:
        """Convert bytes back into a list of records.

        Args:
            data: bytes produced by serialize().

        Returns:
            List of dicts, matching the original structure.

        Raises:
            DeserializationError: if the bytes are corrupt or wrong format.
        """
        ...

    def get_mime_type(self) -> str:
        """Return the MIME type for HTTP Content-Type headers.

        Example: 'application/json', 'text/csv', 'application/xml'
        """
        ...

    def get_extension(self) -> str:
        """Return the file extension without the dot.

        Example: 'json', 'xml', 'parquet', 'csv'
        """
        ...


class SerializerFactory(ABC):
    """Creator — declares the factory method that subclasses override.

    OCP: adding a new format (e.g. MessagePack) = new ConcreteCreator in
    infrastructure/, zero changes here.
    DIP: this ABC and the Protocol are the only things high-level code imports.
    """

    @abstractmethod
    def create_serializer(self) -> DataSerializer:
        """Factory method: return a DataSerializer for this format.

        Returns:
            A configured DataSerializer ready to use.
        """
        ...

    def get_format_name(self) -> str:
        """Human-readable format name for display in the UI."""
        return self.__class__.__name__.replace("SerializerFactory", "")

    def round_trip(self, data: list[dict[str, object]]) -> list[dict[str, object]]:
        """Template method: serialize then deserialize (useful for testing).

        Concrete serializers don't need to implement this; only the
        factory method is overridden.

        Args:
            data: list of records to round-trip.

        Returns:
            Deserialized records (should equal original data).
        """
        serializer = self.create_serializer()
        raw = serializer.serialize(data)
        return serializer.deserialize(raw)
