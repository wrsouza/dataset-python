"""Strategy ABC for the Compression Strategy CLI."""

from __future__ import annotations

from abc import ABC, abstractmethod


class CompressionStrategy(ABC):
    """Abstract base for all compression strategies.

    OCP: add a new codec = new subclass, no existing code changes.
    LSP: all subclasses round-trip compress/decompress for any bytes.
    """

    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        """Compress the given bytes."""
        ...

    @abstractmethod
    def decompress(self, data: bytes) -> bytes:
        """Decompress bytes previously produced by `compress`."""
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Return the canonical name of this strategy."""
        ...

    @abstractmethod
    def get_file_extension(self) -> str:
        """Return the file extension this strategy's output uses."""
        ...
