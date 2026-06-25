"""Bridge interfaces: the Implementor side of the pattern.

`FormatExporter` is the Implementor — it defines the low-level operation
(serializing a Report to bytes for a specific format). The Abstraction side
(`ReportExporter` in `application/use_cases.py`) holds a reference to a
`FormatExporter` and delegates the actual encoding to it, so abstraction and
implementation can vary independently.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from exporter.domain.entities import Report


class FormatExporter(ABC):
    """Implementor: encodes a Report into a specific file format."""

    @abstractmethod
    def serialize(self, report: Report) -> bytes:
        """Encode the report into the target format and return raw bytes."""

    @abstractmethod
    def file_extension(self) -> str:
        """Return the conventional file extension for this format (no dot)."""

    @abstractmethod
    def format_name(self) -> str:
        """Return a short human-readable name for this format."""
