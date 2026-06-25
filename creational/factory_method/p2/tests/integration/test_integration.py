"""Integration tests for P2 — File Storage Factory (Flask routes)."""
from __future__ import annotations

import io
import pytest

from storage.main import app
from storage.infrastructure.creators import GCSStorageClient


@pytest.fixture(autouse=True)
def clear_gcs_store() -> None:
    """Reset GCS in-memory store before each integration test."""
    GCSStorageClient._store.clear()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestUploadDownloadDelete:
    def test_upload_to_gcs(self, client) -> None:
        data = b"integration test content"
        response = client.post(
            "/files/gcs",
            data={"file": (io.BytesIO(data), "test.txt"), "key": "test.txt"},
            content_type="multipart/form-data",
        )
        assert response.status_code == 201
        body = response.get_json()
        assert body["provider"] == "GCS"
        assert body["key"] == "test.txt"

    def test_download_from_gcs(self, client) -> None:
        data = b"download me"
        client.post(
            "/files/gcs",
            data={"file": (io.BytesIO(data), "dl.txt"), "key": "dl.txt"},
            content_type="multipart/form-data",
        )
        response = client.get("/files/gcs/dl.txt")
        assert response.status_code == 200
        assert response.data == data

    def test_delete_from_gcs(self, client) -> None:
        data = b"to be deleted"
        client.post(
            "/files/gcs",
            data={"file": (io.BytesIO(data), "del.txt"), "key": "del.txt"},
            content_type="multipart/form-data",
        )
        response = client.delete("/files/gcs/del.txt")
        assert response.status_code == 200

        response = client.get("/files/gcs/del.txt")
        assert response.status_code == 404

    def test_unknown_provider_returns_404(self, client) -> None:
        response = client.get("/files/ftp/some_key")
        assert response.status_code == 404

    def test_list_providers(self, client) -> None:
        response = client.get("/providers")
        assert response.status_code == 200
        slugs = {p["slug"] for p in response.get_json()}
        assert "gcs" in slugs
        assert "local" in slugs
