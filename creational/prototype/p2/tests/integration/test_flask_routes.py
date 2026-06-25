"""Integration tests for Flask routes using mongomock."""
from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest

from documents.domain.entities import TemplateNotFoundError


@pytest.fixture
def client():
    """Create a Flask test client with mocked MongoDB."""
    with patch("main.template_repo") as mock_template_repo, \
         patch("main.document_repo") as mock_document_repo:
        from main import app
        app.config["TESTING"] = True
        with app.test_client() as c:
            yield c, mock_template_repo, mock_document_repo


def test_list_templates_empty(client):
    test_client, template_repo, _ = client
    template_repo.find_all.return_value = []
    response = test_client.get("/templates")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_template_missing_fields(client):
    test_client, _, _ = client
    response = test_client.post("/templates", json={})
    assert response.status_code == 400


def test_clone_document_not_found(client):
    test_client, template_repo, document_repo = client
    template_repo.find_by_id.side_effect = TemplateNotFoundError("bad_id")
    response = test_client.post(
        "/documents/clone/bad_id", json={"substitutions": {}}
    )
    assert response.status_code == 404
