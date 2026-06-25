"""Domain interfaces (Subject) for the Access Control Proxy pattern.

DocumentService is the Subject role.
Both PostgresDocumentService (RealSubject) and PermissionProxy (Proxy)
implement this Protocol, ensuring LSP and DIP.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from access_control.domain.entities import Document


@runtime_checkable
class DocumentService(Protocol):
    """Subject: contract for document CRUD operations.

    All callers (views, use cases) depend on this Protocol only.
    The middleware transparently injects either the real service or
    the permission proxy — clients never know which they hold.
    """

    def get(self, doc_id: str) -> Document:
        """Return the document with the given ID."""
        ...

    def create(self, data: dict[str, str]) -> Document:
        """Create a new document from data and return it."""
        ...

    def update(self, doc_id: str, data: dict[str, str]) -> Document:
        """Update an existing document and return the updated version."""
        ...

    def delete(self, doc_id: str) -> None:
        """Soft-delete the document with the given ID."""
        ...

    def list(self, filters: dict[str, str]) -> list[Document]:
        """Return documents matching the given filters."""
        ...


class AuditLogger(Protocol):
    """Records every access decision — granted or denied."""

    def log(
        self, user_id: str, action: str, resource_id: str, granted: bool, reason: str
    ) -> None: ...
