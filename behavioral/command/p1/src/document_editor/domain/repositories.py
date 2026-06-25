"""Repository abstractions for persisting documents and command history.

Kept separate from `interfaces.py` (which defines the Command pattern
roles) so the pattern-specific contracts are not mixed with persistence
contracts (Interface Segregation).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from document_editor.domain.entities import CommandInfo, Document


class DocumentRepository(ABC):
    """Persists and retrieves Document aggregates."""

    @abstractmethod
    def get(self, document_id: str) -> Document | None:
        """Return the document with `document_id`, or None if absent."""
        ...

    @abstractmethod
    def save(self, document: Document) -> None:
        """Persist the given document, creating or updating it."""
        ...


class CommandHistoryRepository(ABC):
    """Persists the command history log for a document."""

    @abstractmethod
    def append(self, document_id: str, info: CommandInfo, action: str) -> None:
        """Record one history entry (action is 'execute', 'undo' or 'redo')."""
        ...

    @abstractmethod
    def list_for_document(self, document_id: str) -> list[CommandInfo]:
        """Return all history entries recorded for `document_id`."""
        ...
