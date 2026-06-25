"""Proxy: PermissionProxy — Protection Proxy implementation.

Pattern roles:
  - Subject:     DocumentService (Protocol in domain/interfaces.py)
  - RealSubject: DjangoDocumentService (infrastructure/real_subject.py)
  - Proxy:       PermissionProxy (this file)

Checks the current user's role before delegating to the RealSubject, and
records every access decision via AuditLogger — granted or denied.
Clients (views, use cases) depend on DocumentService only, so they cannot
tell whether they are holding the Proxy or the RealSubject.
"""

from __future__ import annotations

from access_control.domain.entities import Document, Role, User
from access_control.domain.exceptions import InactiveUserError, PermissionDeniedError
from access_control.domain.interfaces import AuditLogger, DocumentService

_ROLE_PERMISSIONS: dict[Role, frozenset[str]] = {
    Role.GUEST: frozenset(),
    Role.VIEWER: frozenset({"read"}),
    Role.EDITOR: frozenset({"read", "write"}),
    Role.OWNER: frozenset({"read", "write", "delete"}),
}


class PermissionProxy:
    """Protection Proxy: verifies permission, then delegates to the RealSubject."""

    def __init__(
        self, real_service: DocumentService, user: User, audit_logger: AuditLogger
    ) -> None:
        self._real = real_service
        self._user = user
        self._audit = audit_logger

    def get(self, doc_id: str) -> Document:
        self._authorize("read", doc_id)
        return self._real.get(doc_id)

    def create(self, data: dict[str, str]) -> Document:
        self._authorize("write", "*")
        return self._real.create(data)

    def update(self, doc_id: str, data: dict[str, str]) -> Document:
        self._authorize("write", doc_id)
        return self._real.update(doc_id, data)

    def delete(self, doc_id: str) -> None:
        self._authorize("delete", doc_id)
        self._real.delete(doc_id)

    def list(self, filters: dict[str, str]) -> list[Document]:
        self._authorize("read", "*")
        return self._real.list(filters)

    def _authorize(self, action: str, resource_id: str) -> None:
        """Raise InactiveUserError/PermissionDeniedError or return silently.

        Every decision — granted or denied — is recorded via AuditLogger,
        which is itself injected (DIP), keeping the Proxy free of any direct
        persistence dependency.
        """
        if not self._user.is_active:
            self._audit.log(
                self._user.user_id, action, resource_id, False, "inactive user"
            )
            raise InactiveUserError(self._user.user_id)

        allowed_actions = _ROLE_PERMISSIONS.get(self._user.role, frozenset())
        granted = action in allowed_actions
        reason = "" if granted else f"role {self._user.role.value} lacks {action!r}"
        self._audit.log(self._user.user_id, action, resource_id, granted, reason)

        if not granted:
            raise PermissionDeniedError(self._user.user_id, action, resource_id)
