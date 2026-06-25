"""Domain entities for the Text Editor Undo/Redo system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class TextSnapshot:
    """Immutable snapshot of the document's content at a point in time.

    frozen=True enforces the Memento pattern guarantee: once captured,
    a snapshot cannot be mutated — only read or discarded.
    """

    content: str
    version: int
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError(f"version must be >= 1, got {self.version}")


@dataclass
class TextDocument:
    """Originator — holds the current text content and produces/restores
    snapshots.

    SRP: TextDocument only manages its own content. It does not persist
    itself — that is the Caretaker's job.
    """

    content: str = ""
    current_version: int = 0

    def create_snapshot(self, version: int) -> TextSnapshot:
        """Capture current content into an immutable TextSnapshot."""
        return TextSnapshot(content=self.content, version=version)

    def restore(self, snapshot: TextSnapshot) -> None:
        """Restore content from a previously captured snapshot.

        The TextDocument does not know how the snapshot was stored —
        that is the Caretaker's concern (Separation of Concerns / SRP).
        """
        self.content = snapshot.content
        self.current_version = snapshot.version

    def write(self, content: str) -> None:
        """Replace the document's content."""
        self.content = content


class NoHistoryError(Exception):
    """Raised when undo/redo is requested but no step is available."""

    def __init__(self, action: str) -> None:
        super().__init__(f"Nothing to {action}")
        self.action = action
