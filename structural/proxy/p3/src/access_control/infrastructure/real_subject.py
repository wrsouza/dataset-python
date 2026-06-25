"""RealSubject: DjangoDocumentService — performs actual ORM operations.

This is the "real" implementation the PermissionProxy wraps. It has no
knowledge of users, roles, or permissions — that is entirely the Proxy's
responsibility (SRP).
"""

from __future__ import annotations

from access_control.domain.entities import Document
from access_control.domain.exceptions import DocumentNotFoundError
from access_control.infrastructure.models import DocumentModel


class DjangoDocumentService:
    """RealSubject: CRUD operations against PostgreSQL via the Django ORM."""

    def get(self, doc_id: str) -> Document:
        model = self._find_or_raise(doc_id)
        return self._to_domain(model)

    def create(self, data: dict[str, str]) -> Document:
        model = DocumentModel.objects.create(
            doc_id=data["doc_id"],
            title=data["title"],
            content=data["content"],
            owner_id=data["owner_id"],
        )
        return self._to_domain(model)

    def update(self, doc_id: str, data: dict[str, str]) -> Document:
        model = self._find_or_raise(doc_id)
        if "title" in data:
            model.title = data["title"]
        if "content" in data:
            model.content = data["content"]
        model.save()
        return self._to_domain(model)

    def delete(self, doc_id: str) -> None:
        model = self._find_or_raise(doc_id)
        model.is_deleted = True
        model.save()

    def list(self, filters: dict[str, str]) -> list[Document]:
        queryset = DocumentModel.objects.filter(is_deleted=False)
        owner_id = filters.get("owner_id")
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)
        return [self._to_domain(model) for model in queryset]

    def _find_or_raise(self, doc_id: str) -> DocumentModel:
        try:
            return DocumentModel.objects.get(doc_id=doc_id, is_deleted=False)
        except DocumentModel.DoesNotExist as exc:
            raise DocumentNotFoundError(doc_id) from exc

    def _to_domain(self, model: DocumentModel) -> Document:
        return Document(
            doc_id=model.doc_id,
            title=model.title,
            content=model.content,
            owner_id=model.owner_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_deleted=model.is_deleted,
        )
