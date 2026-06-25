"""Integration tests for Django views — exercises the full HTTP stack.

Uses Django test client (no real HTTP server needed).
GCS and Azure adapters use fake clients.  S3 is mocked via patch.
"""

from __future__ import annotations

import io
import json
from unittest.mock import MagicMock, patch

import django
import pytest
from django.test import Client, TestCase

# Django settings must be configured before importing models/views
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cloud_adapter.settings")
django.setup()

from cloud_adapter.web.models import FileUpload  # noqa: E402


@pytest.fixture(autouse=True)
def _migrate_db(django_db_setup: None) -> None:  # type: ignore[type-arg]
    """Ensure DB tables exist for each test."""


@pytest.mark.django_db
class TestUploadView(TestCase):
    def _upload(self, provider: str, content: bytes = b"test data") -> "django.http.HttpResponse":
        return self.client.post(
            f"/files/upload?provider={provider}",
            data={"file": io.BytesIO(content)},
            format="multipart",
        )

    def test_upload_gcs_returns_201(self) -> None:
        response = self._upload("gcs")
        assert response.status_code == 201
        body = json.loads(response.content)
        assert body["provider"] == "gcs"
        assert body["size"] == len(b"test data")

    def test_upload_azure_returns_201(self) -> None:
        response = self._upload("azure")
        assert response.status_code == 201
        body = json.loads(response.content)
        assert body["provider"] == "azure"

    def test_upload_invalid_provider_returns_400(self) -> None:
        response = self._upload("dropbox")
        assert response.status_code == 400

    def test_upload_without_file_returns_400(self) -> None:
        response = self.client.post("/files/upload?provider=gcs", data={})
        assert response.status_code == 400


@pytest.mark.django_db
class TestListView(TestCase):
    def test_list_all_files(self) -> None:
        FileUpload.objects.create(key="a.txt", provider="gcs", size=10, url="http://x/a")
        FileUpload.objects.create(key="b.txt", provider="azure", size=20, url="http://x/b")
        response = self.client.get("/files/")
        assert response.status_code == 200
        body = json.loads(response.content)
        assert body["count"] == 2

    def test_list_filtered_by_provider(self) -> None:
        FileUpload.objects.create(key="g.txt", provider="gcs", size=5, url="http://x/g")
        FileUpload.objects.create(key="a.txt", provider="azure", size=5, url="http://x/a")
        response = self.client.get("/files/?provider=gcs")
        body = json.loads(response.content)
        assert body["count"] == 1
        assert body["files"][0]["provider"] == "gcs"

    def test_list_invalid_provider_returns_400(self) -> None:
        response = self.client.get("/files/?provider=dropbox")
        assert response.status_code == 400


@pytest.mark.django_db
class TestDeleteView(TestCase):
    def test_delete_existing_record_returns_204(self) -> None:
        record = FileUpload.objects.create(key="del.txt", provider="gcs", size=3, url="http://x")
        with patch("cloud_adapter.web.views.make_storage") as mock_factory:
            mock_storage = MagicMock()
            mock_factory.return_value = mock_storage
            response = self.client.delete(f"/files/{record.pk}")
        assert response.status_code == 204
        assert not FileUpload.objects.filter(pk=record.pk).exists()

    def test_delete_nonexistent_returns_404(self) -> None:
        response = self.client.delete("/files/99999")
        assert response.status_code == 404
