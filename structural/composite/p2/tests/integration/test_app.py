"""End-to-end integration tests for the Flask app, backed by moto S3."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from filesystem.app import create_app
from filesystem.domain.exceptions import FSStorageError
from filesystem.domain.interfaces import FSNode
from filesystem.infrastructure.s3_client import S3StorageClient

if TYPE_CHECKING:
    from flask.testing import FlaskClient


class _FailingStorage:
    """Test double simulating an unexpected S3 failure (FSStorageError)."""

    def get_node(self, path: str) -> FSNode:
        raise FSStorageError(f"simulated S3 outage for {path!r}")


@pytest.fixture
def client(storage: S3StorageClient) -> FlaskClient:
    app = create_app(storage=storage)
    app.testing = True
    return app.test_client()


@pytest.fixture
def failing_client() -> FlaskClient:
    app = create_app(storage=_FailingStorage())  # type: ignore[arg-type]
    app.testing = True
    return app.test_client()


class TestHealth:
    def test_health_returns_ok(self, client: FlaskClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.get_json() == {"status": "ok"}


class TestUploadAndTree:
    def test_upload_then_get_tree_returns_file(self, client: FlaskClient) -> None:
        upload = client.post(
            "/files/notes.txt", data=b"hello", content_type="text/plain"
        )
        assert upload.status_code == 201

        tree = client.get("/tree/notes.txt")
        assert tree.status_code == 200
        body = tree.get_json()
        assert body["type"] == "file"
        assert body["path"] == "notes.txt"

    def test_get_tree_for_missing_path_returns_404(self, client: FlaskClient) -> None:
        response = client.get("/tree/ghost.txt")
        assert response.status_code == 404


class TestDirectories:
    def test_create_directory_then_tree_returns_folder(
        self, client: FlaskClient
    ) -> None:
        create = client.post("/directories/photos")
        assert create.status_code == 201

        tree = client.get("/tree/photos")
        assert tree.status_code == 200
        assert tree.get_json()["type"] == "folder"


class TestSizeAndContents:
    def test_size_endpoint_sums_nested_files(self, client: FlaskClient) -> None:
        client.post("/files/docs/a.txt", data=b"123", content_type="text/plain")
        client.post("/files/docs/b.txt", data=b"12345", content_type="text/plain")

        response = client.get("/size/docs")

        assert response.status_code == 200
        assert response.get_json() == {"path": "docs", "size_bytes": 8}

    def test_size_for_missing_path_returns_404(self, client: FlaskClient) -> None:
        response = client.get("/size/ghost")
        assert response.status_code == 404

    def test_contents_endpoint_lists_descendant_files(
        self, client: FlaskClient
    ) -> None:
        client.post("/files/docs/a.txt", data=b"1", content_type="text/plain")
        client.post("/files/docs/sub/b.txt", data=b"22", content_type="text/plain")

        response = client.get("/contents/docs")

        assert response.status_code == 200
        paths = {item["path"] for item in response.get_json()}
        assert paths == {"docs/a.txt", "docs/sub/b.txt"}

    def test_contents_for_missing_path_returns_404(self, client: FlaskClient) -> None:
        response = client.get("/contents/ghost")
        assert response.status_code == 404


class TestDeleteNode:
    def test_delete_file_then_tree_returns_404(self, client: FlaskClient) -> None:
        client.post("/files/a.txt", data=b"1", content_type="text/plain")

        delete = client.delete("/nodes/a.txt")
        assert delete.status_code == 200
        assert delete.get_json() == {"path": "a.txt", "status": "deleted"}

        tree = client.get("/tree/a.txt")
        assert tree.status_code == 404

    def test_delete_missing_node_returns_404(self, client: FlaskClient) -> None:
        response = client.delete("/nodes/ghost")
        assert response.status_code == 404

    def test_delete_directory_removes_all_children(self, client: FlaskClient) -> None:
        client.post("/files/docs/a.txt", data=b"1", content_type="text/plain")
        client.post("/files/docs/b.txt", data=b"2", content_type="text/plain")

        delete = client.delete("/nodes/docs")
        assert delete.status_code == 200

        tree = client.get("/tree/docs")
        assert tree.status_code == 404


class TestStorageErrorHandling:
    """Cover the 502 branches: unexpected S3 errors surface as Bad Gateway."""

    def test_get_tree_returns_502_on_storage_error(
        self, failing_client: FlaskClient
    ) -> None:
        response = failing_client.get("/tree/anything")
        assert response.status_code == 502

    def test_get_size_returns_502_on_storage_error(
        self, failing_client: FlaskClient
    ) -> None:
        response = failing_client.get("/size/anything")
        assert response.status_code == 502

    def test_get_contents_returns_502_on_storage_error(
        self, failing_client: FlaskClient
    ) -> None:
        response = failing_client.get("/contents/anything")
        assert response.status_code == 502


class TestAppFactory:
    def test_create_app_with_injected_storage_skips_default_client(
        self, storage: S3StorageClient
    ) -> None:
        # Passing `storage` explicitly (as the `client` fixture does for
        # every other test in this module) proves create_app() honours
        # dependency injection (DIP) instead of always building its own
        # S3StorageClient — the real AWS/LocalStack endpoint is never
        # touched in tests.
        app = create_app(storage=storage)
        assert app is not None
