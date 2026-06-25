"""Integration tests for the Django HTTP endpoint.

Uses Django's test client against a real test database created by
pytest-django (`@pytest.mark.django_db`), exercising the full
request -> view -> use case -> decorator stack -> ORM path.
"""

from __future__ import annotations

import json
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_test")
django.setup()

import pytest
from django.test import Client

from permission_layers.models import AccessLogModel, DocumentModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture(autouse=True)
def seed_document() -> None:
    DocumentModel.objects.create(
        resource_id="doc-1", owner_id="owner-1", title="Q3 Report"
    )


def _evaluate_payload(**overrides: object) -> str:
    payload: dict[str, object] = {
        "user_id": "owner-1",
        "username": "alice",
        "roles": [],
        "is_authenticated": True,
        "resource_id": "doc-1",
        "owner_id": "owner-1",
        "title": "Q3 Report",
        "action": "read",
        "required_role": None,
    }
    payload.update(overrides)
    return json.dumps(payload)


def test_evaluate_access_grants_owner_read(client: Client) -> None:
    response = client.post(
        "/access/evaluate",
        data=_evaluate_payload(),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data["granted"] is True
    assert "audit_log" in data["layers_applied"]


def test_evaluate_access_denies_anonymous(client: Client) -> None:
    response = client.post(
        "/access/evaluate",
        data=_evaluate_payload(user_id="", username="anon", is_authenticated=False),
        content_type="application/json",
    )
    assert response.status_code == 403
    data = json.loads(response.content)
    assert data["granted"] is False


def test_evaluate_access_denies_write_for_non_owner(client: Client) -> None:
    response = client.post(
        "/access/evaluate",
        data=_evaluate_payload(user_id="stranger", username="bob", action="write"),
        content_type="application/json",
    )
    assert response.status_code == 403
    data = json.loads(response.content)
    assert "require_ownership" in data["layers_applied"]


def test_evaluate_access_grants_write_for_owner(client: Client) -> None:
    response = client.post(
        "/access/evaluate",
        data=_evaluate_payload(action="write"),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert data["granted"] is True


def test_evaluate_access_persists_audit_log_row(client: Client) -> None:
    client.post(
        "/access/evaluate",
        data=_evaluate_payload(),
        content_type="application/json",
    )
    assert AccessLogModel.objects.filter(resource_id="doc-1").exists()


def test_evaluate_access_with_get_returns_405(client: Client) -> None:
    response = client.get("/access/evaluate")
    assert response.status_code == 405


def test_evaluate_access_denies_missing_role(client: Client) -> None:
    response = client.post(
        "/access/evaluate",
        data=_evaluate_payload(required_role="admin"),
        content_type="application/json",
    )
    assert response.status_code == 403
    data = json.loads(response.content)
    assert "require_role" in data["layers_applied"]
