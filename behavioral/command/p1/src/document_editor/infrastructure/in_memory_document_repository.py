"""In-memory repository adapters used by unit tests and local exploration.

Swappable with the PostgreSQL adapters without touching application code,
since both implement the same `domain.repositories` abstractions (LSP/DIP).
"""

from __future__ import annotations

from document_editor.domain.entities import CommandInfo, Document
from document_editor.domain.repositories import (
    CommandHistoryRepository,
    DocumentRepository,
)


class InMemoryDocumentRepository(DocumentRepository):
    """Keeps documents in a plain dict; useful for tests and demos."""

    def __init__(self) -> None:
        self._documents: dict[str, Document] = {}

    def get(self, document_id: str) -> Document | None:
        return self._documents.get(document_id)

    def save(self, document: Document) -> None:
        self._documents[document.document_id] = document


class InMemoryCommandHistoryRepository(CommandHistoryRepository):
    """Keeps history entries in a plain list; useful for tests and demos."""

    def __init__(self) -> None:
        self._entries: list[tuple[str, CommandInfo, str]] = []

    def append(self, document_id: str, info: CommandInfo, action: str) -> None:
        self._entries.append((document_id, info, action))

    def list_for_document(self, document_id: str) -> list[CommandInfo]:
        return [info for doc_id, info, _ in self._entries if doc_id == document_id]
