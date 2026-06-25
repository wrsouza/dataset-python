"""Domain entities and value objects for the Document Editor domain."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from document_editor.domain.interfaces import DocumentReceiver


class FormatType(StrEnum):
    """Supported inline text formats."""

    BOLD = "bold"
    ITALIC = "italic"
    UNDERLINE = "underline"


@dataclass
class FormatRange:
    """A formatting annotation applied to a span of text."""

    start: int
    end: int
    format_type: FormatType


@dataclass
class Document(DocumentReceiver):
    """Mutable aggregate holding the text content and formatting state.

    This is the Receiver in the Command pattern: it knows how to perform
    the low-level mutations (insert, delete, format) but has no notion
    of history, undo or redo — that responsibility belongs to the Invoker.
    """

    document_id: str
    content: str = ""
    format_ranges: list[FormatRange] = field(default_factory=list)

    def get_content(self) -> str:
        """Return the current document content."""
        return self.content

    def insert(self, position: int, text: str) -> None:
        """Insert `text` at `position`, raising on an out-of-range index."""
        if not 0 <= position <= len(self.content):
            raise InvalidPositionError(position, len(self.content))
        self.content = self.content[:position] + text + self.content[position:]

    def delete(self, start: int, end: int) -> str:
        """Delete characters in [start, end) and return the removed text."""
        self._validate_range(start, end)
        deleted = self.content[start:end]
        self.content = self.content[:start] + self.content[end:]
        return deleted

    def get_formatted_ranges(self) -> list[dict[str, object]]:
        """Return active formatting ranges as plain dictionaries."""
        return [
            {"start": r.start, "end": r.end, "format_type": r.format_type.value}
            for r in self.format_ranges
        ]

    def apply_format(self, start: int, end: int, format_type: str) -> None:
        """Add a formatting range over [start, end)."""
        self._validate_range(start, end)
        self.format_ranges.append(
            FormatRange(start=start, end=end, format_type=FormatType(format_type))
        )

    def remove_format(self, start: int, end: int, format_type: str) -> None:
        """Remove a previously applied formatting range, if present."""
        target = FormatType(format_type)
        self.format_ranges = [
            r
            for r in self.format_ranges
            if not (r.start == start and r.end == end and r.format_type == target)
        ]

    def _validate_range(self, start: int, end: int) -> None:
        if not 0 <= start <= end <= len(self.content):
            raise InvalidRangeError(start, end, len(self.content))


class InvalidPositionError(ValueError):
    """Raised when an insert position falls outside the document bounds."""

    def __init__(self, position: int, content_length: int) -> None:
        self.position = position
        self.content_length = content_length
        super().__init__(
            f"Position {position} is out of bounds for document of "
            f"length {content_length}"
        )


class InvalidRangeError(ValueError):
    """Raised when a [start, end) range falls outside the document bounds."""

    def __init__(self, start: int, end: int, content_length: int) -> None:
        self.start = start
        self.end = end
        self.content_length = content_length
        super().__init__(
            f"Range [{start}, {end}) is invalid for document of "
            f"length {content_length}"
        )


@dataclass(frozen=True)
class CommandResult:
    """Outcome of executing or undoing a command."""

    success: bool
    message: str
    content_snapshot: str


@dataclass(frozen=True)
class CommandInfo:
    """Read-only summary of a command entry in the history."""

    command_id: str
    description: str
    is_reversible: bool
    executed_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    @staticmethod
    def new_id() -> str:
        """Generate a fresh unique identifier for a command entry."""
        return str(uuid.uuid4())
