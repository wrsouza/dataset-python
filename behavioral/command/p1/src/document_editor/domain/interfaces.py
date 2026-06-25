"""Domain interfaces for the Document Editor Command pattern.

Defines the Command ABC, Receiver ABC, and Invoker ABC following
Open/Closed and Single Responsibility principles.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from document_editor.domain.entities import CommandInfo, CommandResult


class DocumentCommand(ABC):
    """Abstract base for all document editing commands.

    Each concrete command encapsulates a single reversible operation
    on a document. Adding a new operation requires only a new subclass —
    no changes to existing code (OCP).
    """

    @abstractmethod
    def execute(self) -> CommandResult:
        """Apply the command to the receiver."""
        ...

    @abstractmethod
    def undo(self) -> CommandResult:
        """Revert the command, restoring previous state."""
        ...

    @abstractmethod
    def get_description(self) -> str:
        """Human-readable description of this command."""
        ...

    @abstractmethod
    def is_reversible(self) -> bool:
        """Return True if this command supports undo."""
        ...


class DocumentReceiver(ABC):
    """Abstract receiver that owns the document state and mutation logic."""

    @abstractmethod
    def get_content(self) -> str:
        """Return the current document content."""
        ...

    @abstractmethod
    def insert(self, position: int, text: str) -> None:
        """Insert text at the given position."""
        ...

    @abstractmethod
    def delete(self, start: int, end: int) -> str:
        """Delete characters from start to end; returns deleted text."""
        ...

    @abstractmethod
    def get_formatted_ranges(self) -> list[dict[str, object]]:
        """Return list of active formatting ranges."""
        ...

    @abstractmethod
    def apply_format(self, start: int, end: int, format_type: str) -> None:
        """Apply formatting to the range [start, end)."""
        ...

    @abstractmethod
    def remove_format(self, start: int, end: int, format_type: str) -> None:
        """Remove formatting from the range [start, end)."""
        ...


class CommandInvoker(ABC):
    """Abstract invoker that manages the command history."""

    @abstractmethod
    def execute(self, command: DocumentCommand) -> CommandResult:
        """Execute a command and record it in history."""
        ...

    @abstractmethod
    def undo(self) -> CommandResult | None:
        """Undo the most recent reversible command."""
        ...

    @abstractmethod
    def redo(self) -> CommandResult | None:
        """Redo the most recently undone command."""
        ...

    @abstractmethod
    def get_history(self) -> list[CommandInfo]:
        """Return the full command history for the document."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear the entire command history."""
        ...
