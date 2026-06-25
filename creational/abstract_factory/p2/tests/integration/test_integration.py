"""Integration tests for the Cloud Storage Factory FastAPI.

Uses GCS and Azure fakes (no LocalStack needed).
For AWS tests, run with LocalStack via docker-compose.
"""
from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    from cloud_storage.app import app
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.parametrize("provider", ["gcs", "azure"])
def test_upload_and_download_roundtrip(client: TestClient, provider: str) -> None:
    content = b"integration test content"
    upload_response = client.post(
        "/upload",
        params={"provider": provider, "key": f"integration/{provider}/test.txt"},
        files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
    )
    assert upload_response.status_code == 200
    result = upload_response.json()
    assert result["provider"] == provider
    assert result["size_bytes"] == len(content)


@pytest.mark.parametrize("provider", ["gcs", "azure"])
def test_signed_url_generation(client: TestClient, provider: str) -> None:
    response = client.get(
        f"/signed-url/some/object.txt",
        params={"provider": provider, "expires_in": 600},
    )
    assert response.status_code == 200
    data = response.json()
    assert "signed_url" in data
    assert data["expires_in_seconds"] == 600
    assert data["provider"] == provider


def test_download_nonexistent_returns_404(client: TestClient) -> None:
    response = client.get(
        "/download/nonexistent/key.txt",
        params={"provider": "gcs"},
    )
    assert response.status_code == 404


def test_invalid_provider_returns_400(client: TestClient) -> None:
    response = client.get("/metadata/some/key", params={"provider": "dropbox"})
    assert response.status_code == 400
