"""Integration tests exercising the FastAPI app end-to-end via TestClient.

Decision: these tests run against a SQLite in-memory database (see the
`client` fixture in conftest.py) rather than a real PostgreSQL instance,
so the suite is self-contained and does not require docker-compose to be
running. The repository classes under test only use portable SQLAlchemy
ORM features, so the behavior verified here matches production.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestDocumentLifecycle:
    def test_get_unknown_document_creates_empty_document(
        self, client: TestClient
    ) -> None:
        response = client.get("/documents/doc-1")

        assert response.status_code == 200
        assert response.json() == {
            "document_id": "doc-1",
            "content": "",
            "format_ranges": [],
        }

    def test_insert_then_get_reflects_new_content(self, client: TestClient) -> None:
        client.post("/documents/doc-1/insert", json={"position": 0, "text": "hello"})

        response = client.get("/documents/doc-1")

        assert response.json()["content"] == "hello"

    def test_insert_invalid_position_returns_400(self, client: TestClient) -> None:
        response = client.post(
            "/documents/doc-1/insert", json={"position": 50, "text": "x"}
        )

        assert response.status_code == 400

    def test_delete_removes_text(self, client: TestClient) -> None:
        client.post("/documents/doc-1/insert", json={"position": 0, "text": "hello"})

        response = client.post("/documents/doc-1/delete", json={"start": 0, "end": 2})

        assert response.status_code == 201
        assert response.json()["content_snapshot"] == "llo"

    def test_format_applies_range(self, client: TestClient) -> None:
        client.post("/documents/doc-1/insert", json={"position": 0, "text": "hello"})

        response = client.post(
            "/documents/doc-1/format",
            json={"start": 0, "end": 5, "format_type": "bold"},
        )

        assert response.status_code == 201
        state = client.get("/documents/doc-1").json()
        assert state["format_ranges"] == [{"start": 0, "end": 5, "format_type": "bold"}]


class TestUndoRedo:
    def test_undo_reverts_last_command(self, client: TestClient) -> None:
        client.post("/documents/doc-1/insert", json={"position": 0, "text": "hello"})

        response = client.post("/documents/doc-1/undo")

        assert response.status_code == 200
        assert response.json()["content_snapshot"] == ""

    def test_undo_with_empty_history_returns_409(self, client: TestClient) -> None:
        response = client.post("/documents/doc-1/undo")

        assert response.status_code == 409

    def test_redo_reapplies_undone_command(self, client: TestClient) -> None:
        client.post("/documents/doc-1/insert", json={"position": 0, "text": "hello"})
        client.post("/documents/doc-1/undo")

        response = client.post("/documents/doc-1/redo")

        assert response.status_code == 200
        assert response.json()["content_snapshot"] == "hello"

    def test_redo_with_empty_redo_stack_returns_409(self, client: TestClient) -> None:
        response = client.post("/documents/doc-1/redo")

        assert response.status_code == 409

    def test_history_endpoint_lists_executed_commands(self, client: TestClient) -> None:
        client.post("/documents/doc-1/insert", json={"position": 0, "text": "ab"})
        client.post(
            "/documents/doc-1/format",
            json={"start": 0, "end": 2, "format_type": "italic"},
        )

        response = client.get("/documents/doc-1/history")

        assert response.status_code == 200
        descriptions = [entry["description"] for entry in response.json()]
        assert len(descriptions) == 2
