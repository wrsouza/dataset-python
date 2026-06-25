"""Integration tests: full HTTP request -> middleware -> PermissionProxy -> ORM."""

from __future__ import annotations

import json
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings_test")
django.setup()

from django.test import Client, TestCase  # noqa: E402

from access_control.domain.entities import Role  # noqa: E402
from access_control.infrastructure.models import (  # noqa: E402
    AuditLogModel,
    DocumentModel,
    UserModel,
)


class AccessControlViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        UserModel.objects.create(
            user_id="owner-1", username="alice", email="a@x.com", role=Role.OWNER.value
        )
        UserModel.objects.create(
            user_id="editor-1", username="bob", email="b@x.com", role=Role.EDITOR.value
        )
        UserModel.objects.create(
            user_id="viewer-1",
            username="carol",
            email="c@x.com",
            role=Role.VIEWER.value,
        )
        UserModel.objects.create(
            user_id="guest-1", username="dave", email="d@x.com", role=Role.GUEST.value
        )
        DocumentModel.objects.create(
            doc_id="doc-1", title="Report", content="...", owner_id="owner-1"
        )

    def test_viewer_can_read_document(self) -> None:
        response = self.client.get(
            "/documents/doc-1/", headers={"X-User-Id": "viewer-1"}
        )

        assert response.status_code == 200
        assert json.loads(response.content)["doc_id"] == "doc-1"

    def test_guest_cannot_read_document(self) -> None:
        response = self.client.get(
            "/documents/doc-1/", headers={"X-User-Id": "guest-1"}
        )

        assert response.status_code == 403

    def test_unknown_document_returns_404_for_authorized_user(self) -> None:
        response = self.client.get(
            "/documents/ghost/", headers={"X-User-Id": "owner-1"}
        )

        assert response.status_code == 404

    def test_viewer_cannot_create_document(self) -> None:
        response = self.client.post(
            "/documents/",
            data=json.dumps(
                {"doc_id": "doc-2", "title": "New", "content": "x", "owner_id": "v"}
            ),
            content_type="application/json",
            headers={"X-User-Id": "viewer-1"},
        )

        assert response.status_code == 403

    def test_editor_can_create_document(self) -> None:
        response = self.client.post(
            "/documents/",
            data=json.dumps(
                {
                    "doc_id": "doc-2",
                    "title": "New",
                    "content": "x",
                    "owner_id": "editor-1",
                }
            ),
            content_type="application/json",
            headers={"X-User-Id": "editor-1"},
        )

        assert response.status_code == 201
        assert DocumentModel.objects.filter(doc_id="doc-2").exists()

    def test_editor_cannot_delete_document(self) -> None:
        response = self.client.delete(
            "/documents/doc-1/", headers={"X-User-Id": "editor-1"}
        )

        assert response.status_code == 403

    def test_owner_can_delete_document(self) -> None:
        response = self.client.delete(
            "/documents/doc-1/", headers={"X-User-Id": "owner-1"}
        )

        assert response.status_code == 200

    def test_list_documents_requires_read_permission(self) -> None:
        response = self.client.get("/documents/", headers={"X-User-Id": "guest-1"})

        assert response.status_code == 403

    def test_viewer_can_list_documents(self) -> None:
        response = self.client.get("/documents/", headers={"X-User-Id": "viewer-1"})

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 1

    def test_inactive_user_cannot_create_document(self) -> None:
        UserModel.objects.filter(user_id="owner-1").update(is_active=False)

        response = self.client.post(
            "/documents/",
            data=json.dumps(
                {"doc_id": "doc-3", "title": "T", "content": "C", "owner_id": "x"}
            ),
            content_type="application/json",
            headers={"X-User-Id": "owner-1"},
        )

        assert response.status_code == 403

    def test_owner_can_update_document(self) -> None:
        response = self.client.put(
            "/documents/doc-1/",
            data=json.dumps({"title": "Updated Title"}),
            content_type="application/json",
            headers={"X-User-Id": "owner-1"},
        )

        assert response.status_code == 200
        assert json.loads(response.content)["title"] == "Updated Title"

    def test_update_unknown_document_returns_404(self) -> None:
        response = self.client.put(
            "/documents/ghost/",
            data=json.dumps({"title": "x"}),
            content_type="application/json",
            headers={"X-User-Id": "owner-1"},
        )

        assert response.status_code == 404

    def test_delete_unknown_document_returns_404(self) -> None:
        response = self.client.delete(
            "/documents/ghost/", headers={"X-User-Id": "owner-1"}
        )

        assert response.status_code == 404

    def test_unknown_user_defaults_to_inactive_guest(self) -> None:
        response = self.client.get(
            "/documents/doc-1/", headers={"X-User-Id": "totally-unknown"}
        )

        assert response.status_code == 403

    def test_every_request_creates_an_audit_log_entry(self) -> None:
        self.client.get("/documents/doc-1/", headers={"X-User-Id": "viewer-1"})

        assert AuditLogModel.objects.filter(user_id="viewer-1", granted=True).exists()
