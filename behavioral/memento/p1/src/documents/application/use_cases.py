"""Application use cases for Document Version History.

Each use case has a single responsibility and depends only on abstractions (DIP).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from documents.domain.entities import (
    Document,
    DocumentMemento,
    DocumentNotFoundError,
)
from documents.domain.interfaces import DocumentCaretaker
from documents.infrastructure.repository import DocumentRepository


@dataclass
class CreateDocumentInput:
    id: str
    title: str
    content: str
    metadata: dict[str, Any]
    author: str


@dataclass
class EditDocumentInput:
    document_id: str
    new_content: str
    new_metadata: dict[str, Any]
    author: str


class CreateDocumentUseCase:
    """Creates a new document and saves its initial snapshot.

    SRP: only handles document creation logic.
    DIP: depends on abstractions (repository, caretaker), not concretes.
    """

    def __init__(
        self,
        repository: DocumentRepository,
        caretaker: DocumentCaretaker,
    ) -> None:
        self._repository = repository
        self._caretaker = caretaker

    async def execute(self, data: CreateDocumentInput) -> Document:
        document = Document(
            id=data.id,
            title=data.title,
            content=data.content,
            metadata=data.metadata,
            current_version=1,
        )
        document.set_author(data.author)
        snapshot = document.create_snapshot()
        await self._repository.save(document)
        await self._caretaker.save(document.id, snapshot)
        return document


class EditDocumentUseCase:
    """Edits a document, saving a snapshot of the state BEFORE the edit.

    OCP: new editing strategies can be injected without modifying this class.
    """

    def __init__(
        self,
        repository: DocumentRepository,
        caretaker: DocumentCaretaker,
    ) -> None:
        self._repository = repository
        self._caretaker = caretaker

    async def execute(self, data: EditDocumentInput) -> Document:
        document = await self._repository.find_by_id(data.document_id)
        if document is None:
            raise DocumentNotFoundError(data.document_id)

        document.set_author(data.author)
        document.apply_edit(data.new_content, data.new_metadata)
        snapshot = document.create_snapshot()

        await self._repository.save(document)
        await self._caretaker.save(document.id, snapshot)
        return document


class RestoreVersionUseCase:
    """Restores a document to a specific historical version."""

    def __init__(
        self,
        repository: DocumentRepository,
        caretaker: DocumentCaretaker,
    ) -> None:
        self._repository = repository
        self._caretaker = caretaker

    async def execute(self, document_id: str, version: int) -> Document:
        document = await self._repository.find_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)

        memento = await self._caretaker.get(document_id, version)
        document.restore(memento)
        # Save the restored state as a new version
        document.current_version = await self._repository.next_version(document_id)
        await self._repository.save(document)
        return document


class UndoDocumentUseCase:
    """Reverts a document to the previous snapshot."""

    def __init__(
        self,
        repository: DocumentRepository,
        caretaker: DocumentCaretaker,
    ) -> None:
        self._repository = repository
        self._caretaker = caretaker

    async def execute(self, document_id: str) -> Document:
        document = await self._repository.find_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)

        memento = await self._caretaker.undo(document_id)
        document.restore(memento)
        await self._repository.save(document)
        return document


class GetHistoryUseCase:
    """Returns the full version history of a document."""

    def __init__(self, caretaker: DocumentCaretaker) -> None:
        self._caretaker = caretaker

    async def execute(self, document_id: str) -> list[DocumentMemento]:
        versions = await self._caretaker.list_versions(document_id)
        return [v for v in versions if isinstance(v, DocumentMemento)]
