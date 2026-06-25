"""Domain entities for the Document Version History system."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class DocumentMemento:
    """Immutable snapshot of a document's state at a point in time.

    frozen=True enforces the Memento pattern guarantee: once captured,
    a snapshot cannot be mutated — only read or discarded.
    """

    content: str
    metadata: dict[str, Any]
    version: int
    author: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError(f"version must be >= 1, got {self.version}")
        if not self.author.strip():
            raise ValueError("author cannot be empty")


@dataclass
class Document:
    """Originator — holds current document state and produces/restores snapshots.

    SRP: Document only manages its own content state.
    It does not persist itself — that is the repository's job.
    """

    id: str
    title: str
    content: str
    metadata: dict[str, Any]
    current_version: int = 1
    _author: str = field(default="system", repr=False)

    def set_author(self, author: str) -> None:
        """Set the author for the next snapshot."""
        self._author = author

    def create_snapshot(self) -> DocumentMemento:
        """Capture current state into an immutable DocumentMemento."""
        return DocumentMemento(
            content=self.content,
            metadata=dict(self.metadata),
            version=self.current_version,
            author=self._author,
        )

    def restore(self, memento: DocumentMemento) -> None:
        """Restore document state from a previously captured snapshot.

        The Document does not know how the memento was stored — that is
        the Caretaker's concern (Separation of Concerns / SRP).
        """
        self.content = memento.content
        self.metadata = dict(memento.metadata)
        self.current_version = memento.version

    def apply_edit(self, new_content: str, new_metadata: dict[str, Any]) -> None:
        """Apply new content, incrementing version counter."""
        self.content = new_content
        self.metadata = new_metadata
        self.current_version += 1


class DocumentNotFoundError(Exception):
    """Raised when a document does not exist in the repository."""

    def __init__(self, document_id: str) -> None:
        super().__init__(f"Document '{document_id}' not found")
        self.document_id = document_id


class VersionNotFoundError(Exception):
    """Raised when a requested version does not exist."""

    def __init__(self, document_id: str, version: int) -> None:
        super().__init__(f"Version {version} not found for document '{document_id}'")
        self.document_id = document_id
        self.version = version


class NoHistoryError(Exception):
    """Raised when undo is requested but no previous snapshot exists."""

    def __init__(self, document_id: str) -> None:
        super().__init__(f"No history available for document '{document_id}'")
        self.document_id = document_id
