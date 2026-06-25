"""Unit tests for PermissionProxy — RealSubject and AuditLogger mocked."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from access_control.domain.entities import Document, Role, User
from access_control.domain.exceptions import InactiveUserError, PermissionDeniedError
from access_control.infrastructure.proxy import PermissionProxy


def _make_proxy(
    role: Role, is_active: bool = True
) -> tuple[PermissionProxy, MagicMock, MagicMock]:
    real_service = MagicMock()
    audit_logger = MagicMock()
    user = User(
        user_id="u1",
        username="alice",
        email="a@example.com",
        role=role,
        is_active=is_active,
    )
    proxy = PermissionProxy(
        real_service=real_service, user=user, audit_logger=audit_logger
    )
    return proxy, real_service, audit_logger


def _make_document() -> Document:
    return Document(
        doc_id="doc-1",
        title="Test",
        content="content",
        owner_id="u1",
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )


class TestReadPermission:
    def test_viewer_can_get_document(self) -> None:
        proxy, real_service, _ = _make_proxy(Role.VIEWER)
        real_service.get.return_value = _make_document()

        document = proxy.get("doc-1")

        assert document.doc_id == "doc-1"
        real_service.get.assert_called_once_with("doc-1")

    def test_guest_cannot_get_document(self) -> None:
        proxy, real_service, _ = _make_proxy(Role.GUEST)

        with pytest.raises(PermissionDeniedError):
            proxy.get("doc-1")

        real_service.get.assert_not_called()

    def test_guest_cannot_list_documents(self) -> None:
        proxy, real_service, _ = _make_proxy(Role.GUEST)

        with pytest.raises(PermissionDeniedError):
            proxy.list({})

        real_service.list.assert_not_called()


class TestWritePermission:
    def test_viewer_cannot_create_document(self) -> None:
        proxy, real_service, _ = _make_proxy(Role.VIEWER)

        with pytest.raises(PermissionDeniedError):
            proxy.create({"doc_id": "doc-2"})

        real_service.create.assert_not_called()

    def test_editor_can_create_document(self) -> None:
        proxy, real_service, _ = _make_proxy(Role.EDITOR)
        real_service.create.return_value = _make_document()

        document = proxy.create({"doc_id": "doc-1"})

        assert document.doc_id == "doc-1"

    def test_editor_can_update_document(self) -> None:
        proxy, real_service, _ = _make_proxy(Role.EDITOR)
        real_service.update.return_value = _make_document()

        proxy.update("doc-1", {"title": "New"})

        real_service.update.assert_called_once_with("doc-1", {"title": "New"})


class TestDeletePermission:
    def test_editor_cannot_delete_document(self) -> None:
        proxy, real_service, _ = _make_proxy(Role.EDITOR)

        with pytest.raises(PermissionDeniedError):
            proxy.delete("doc-1")

        real_service.delete.assert_not_called()

    def test_owner_can_delete_document(self) -> None:
        proxy, real_service, _ = _make_proxy(Role.OWNER)

        proxy.delete("doc-1")

        real_service.delete.assert_called_once_with("doc-1")


class TestInactiveUser:
    def test_inactive_owner_cannot_perform_any_action(self) -> None:
        proxy, real_service, _ = _make_proxy(Role.OWNER, is_active=False)

        with pytest.raises(InactiveUserError):
            proxy.get("doc-1")

        real_service.get.assert_not_called()


class TestAuditLogging:
    def test_granted_access_is_logged(self) -> None:
        proxy, real_service, audit_logger = _make_proxy(Role.OWNER)
        real_service.get.return_value = _make_document()

        proxy.get("doc-1")

        audit_logger.log.assert_called_once_with("u1", "read", "doc-1", True, "")

    def test_denied_access_is_logged_with_reason(self) -> None:
        proxy, _, audit_logger = _make_proxy(Role.GUEST)

        with pytest.raises(PermissionDeniedError):
            proxy.get("doc-1")

        audit_logger.log.assert_called_once()
        call_args = audit_logger.log.call_args[0]
        assert call_args[0] == "u1"
        assert call_args[1] == "read"
        assert call_args[3] is False
        assert "GUEST" in call_args[4]

    def test_inactive_user_denial_is_logged(self) -> None:
        proxy, _, audit_logger = _make_proxy(Role.OWNER, is_active=False)

        with pytest.raises(InactiveUserError):
            proxy.get("doc-1")

        audit_logger.log.assert_called_once_with(
            "u1", "read", "doc-1", False, "inactive user"
        )
