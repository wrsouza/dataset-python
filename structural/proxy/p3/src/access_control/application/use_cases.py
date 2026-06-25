"""Application use cases — depend only on the DocumentService Protocol.

Use cases never import DjangoDocumentService or PermissionProxy directly.
Whichever is injected (real or Proxy) is transparent to them (DIP/LSP).
"""

from __future__ import annotations

from access_control.domain.entities import Document
from access_control.domain.interfaces import DocumentService


class GetDocumentUseCase:
    def __init__(self, service: DocumentService) -> None:
        self._service = service

    def execute(self, doc_id: str) -> Document:
        return self._service.get(doc_id)


class CreateDocumentUseCase:
    def __init__(self, service: DocumentService) -> None:
        self._service = service

    def execute(self, data: dict[str, str]) -> Document:
        return self._service.create(data)


class UpdateDocumentUseCase:
    def __init__(self, service: DocumentService) -> None:
        self._service = service

    def execute(self, doc_id: str, data: dict[str, str]) -> Document:
        return self._service.update(doc_id, data)


class DeleteDocumentUseCase:
    def __init__(self, service: DocumentService) -> None:
        self._service = service

    def execute(self, doc_id: str) -> None:
        self._service.delete(doc_id)


class ListDocumentsUseCase:
    def __init__(self, service: DocumentService) -> None:
        self._service = service

    def execute(self, filters: dict[str, str]) -> list[Document]:
        return self._service.list(filters)
