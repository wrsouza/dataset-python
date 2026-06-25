"""Unit tests for the three cloud storage adapters.

All tests run WITHOUT real cloud credentials — GCS and Azure use fake clients,
and S3 uses a mock boto3 client.  This validates the Adapter translation logic.
"""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import pytest

from cloud_adapter.domain.entities import (
    StorageDeleteError,
    StorageDownloadError,
    StorageKeyNotFoundError,
    StorageUploadError,
)
from cloud_adapter.infrastructure.adapters import (
    AzureStorageAdapter,
    GCSStorageAdapter,
    S3StorageAdapter,
)
from cloud_adapter.infrastructure.fake_clients import (
    FakeAzureClient,
    FakeGCSClient,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def gcs_adapter() -> GCSStorageAdapter:
    return GCSStorageAdapter(FakeGCSClient(), "test-bucket")


@pytest.fixture()
def azure_adapter() -> AzureStorageAdapter:
    return AzureStorageAdapter(FakeAzureClient(), "test-container")


@pytest.fixture()
def s3_mock_client() -> MagicMock:
    client = MagicMock()
    # head_bucket raises so create_bucket is called in factory; not needed here
    return client


@pytest.fixture()
def s3_adapter(s3_mock_client: MagicMock) -> S3StorageAdapter:
    return S3StorageAdapter(s3_mock_client, "test-bucket", "http://localstack:4566")


# ── GCS Adapter tests ─────────────────────────────────────────────────────────


class TestGCSStorageAdapter:
    def test_upload_returns_url(self, gcs_adapter: GCSStorageAdapter) -> None:
        url = gcs_adapter.upload("docs/report.pdf", b"PDF content")
        assert "docs/report.pdf" in url or "report.pdf" in url

    def test_download_returns_uploaded_bytes(self, gcs_adapter: GCSStorageAdapter) -> None:
        payload = b"hello gcs"
        gcs_adapter.upload("test.txt", payload)
        result = gcs_adapter.download("test.txt")
        assert result == payload

    def test_download_missing_key_raises_domain_error(self, gcs_adapter: GCSStorageAdapter) -> None:
        with pytest.raises(StorageKeyNotFoundError) as exc_info:
            gcs_adapter.download("nonexistent.bin")
        assert exc_info.value.provider == "gcs"

    def test_delete_removes_key(self, gcs_adapter: GCSStorageAdapter) -> None:
        gcs_adapter.upload("to-delete.txt", b"bye")
        gcs_adapter.delete("to-delete.txt")
        keys = gcs_adapter.list_keys()
        assert "to-delete.txt" not in keys

    def test_list_keys_with_prefix(self, gcs_adapter: GCSStorageAdapter) -> None:
        gcs_adapter.upload("images/cat.png", b"cat")
        gcs_adapter.upload("images/dog.png", b"dog")
        gcs_adapter.upload("docs/readme.md", b"readme")
        keys = gcs_adapter.list_keys(prefix="images/")
        assert set(keys) == {"images/cat.png", "images/dog.png"}

    def test_get_url_format(self, gcs_adapter: GCSStorageAdapter) -> None:
        gcs_adapter.upload("file.bin", b"data")
        url = gcs_adapter.get_url("file.bin")
        assert "storage.googleapis.com" in url

    def test_upload_error_becomes_domain_error(self, gcs_adapter: GCSStorageAdapter) -> None:
        # Patch bucket.blob to raise
        with patch.object(gcs_adapter._client, "bucket", side_effect=RuntimeError("GCS down")):
            with pytest.raises(StorageUploadError) as exc_info:
                gcs_adapter.upload("fail.txt", b"x")
            assert exc_info.value.provider == "gcs"


# ── Azure Adapter tests ───────────────────────────────────────────────────────


class TestAzureStorageAdapter:
    def test_upload_returns_url(self, azure_adapter: AzureStorageAdapter) -> None:
        url = azure_adapter.upload("files/data.csv", b"col1,col2\n1,2")
        assert "blob.core.windows.net" in url

    def test_download_returns_uploaded_bytes(self, azure_adapter: AzureStorageAdapter) -> None:
        payload = b"hello azure"
        azure_adapter.upload("hello.txt", payload)
        result = azure_adapter.download("hello.txt")
        assert result == payload

    def test_download_missing_key_raises_domain_error(self, azure_adapter: AzureStorageAdapter) -> None:
        with pytest.raises(StorageKeyNotFoundError) as exc_info:
            azure_adapter.download("ghost.bin")
        assert exc_info.value.provider == "azure"
        assert exc_info.value.key == "ghost.bin"

    def test_delete_removes_key(self, azure_adapter: AzureStorageAdapter) -> None:
        azure_adapter.upload("temp.txt", b"temp")
        azure_adapter.delete("temp.txt")
        keys = azure_adapter.list_keys()
        assert "temp.txt" not in keys

    def test_list_keys_with_prefix(self, azure_adapter: AzureStorageAdapter) -> None:
        azure_adapter.upload("videos/a.mp4", b"a")
        azure_adapter.upload("videos/b.mp4", b"b")
        azure_adapter.upload("docs/c.docx", b"c")
        keys = azure_adapter.list_keys(prefix="videos/")
        assert set(keys) == {"videos/a.mp4", "videos/b.mp4"}

    def test_get_url_contains_blob_hostname(self, azure_adapter: AzureStorageAdapter) -> None:
        azure_adapter.upload("key.bin", b"k")
        url = azure_adapter.get_url("key.bin")
        assert "blob.core.windows.net" in url


# ── S3 Adapter tests ──────────────────────────────────────────────────────────


class TestS3StorageAdapter:
    def test_upload_calls_put_object(self, s3_adapter: S3StorageAdapter, s3_mock_client: MagicMock) -> None:
        s3_adapter.upload("images/x.png", b"image data")
        s3_mock_client.put_object.assert_called_once_with(
            Bucket="test-bucket", Key="images/x.png", Body=b"image data"
        )

    def test_upload_returns_url_with_key(self, s3_adapter: S3StorageAdapter) -> None:
        url = s3_adapter.upload("folder/file.txt", b"data")
        assert "folder/file.txt" in url

    def test_download_calls_get_object(self, s3_adapter: S3StorageAdapter, s3_mock_client: MagicMock) -> None:
        body_mock = MagicMock()
        body_mock.read.return_value = b"file contents"
        s3_mock_client.get_object.return_value = {"Body": body_mock}
        result = s3_adapter.download("folder/file.txt")
        assert result == b"file contents"

    def test_download_nosuchkey_raises_domain_error(self, s3_adapter: S3StorageAdapter, s3_mock_client: MagicMock) -> None:
        s3_mock_client.get_object.side_effect = Exception("NoSuchKey: The specified key does not exist")
        with pytest.raises(StorageKeyNotFoundError) as exc_info:
            s3_adapter.download("missing.bin")
        assert exc_info.value.provider == "s3"

    def test_delete_calls_delete_object(self, s3_adapter: S3StorageAdapter, s3_mock_client: MagicMock) -> None:
        s3_adapter.delete("old/file.bin")
        s3_mock_client.delete_object.assert_called_once_with(Bucket="test-bucket", Key="old/file.bin")

    def test_list_keys_returns_keys_from_contents(self, s3_adapter: S3StorageAdapter, s3_mock_client: MagicMock) -> None:
        s3_mock_client.list_objects_v2.return_value = {
            "Contents": [{"Key": "a/b.txt"}, {"Key": "a/c.txt"}]
        }
        keys = s3_adapter.list_keys(prefix="a/")
        assert keys == ["a/b.txt", "a/c.txt"]

    def test_list_keys_empty_bucket(self, s3_adapter: S3StorageAdapter, s3_mock_client: MagicMock) -> None:
        s3_mock_client.list_objects_v2.return_value = {}
        keys = s3_adapter.list_keys()
        assert keys == []

    def test_upload_sdk_error_becomes_domain_error(self, s3_adapter: S3StorageAdapter, s3_mock_client: MagicMock) -> None:
        s3_mock_client.put_object.side_effect = Exception("Connection refused")
        with pytest.raises(StorageUploadError) as exc_info:
            s3_adapter.upload("fail.txt", b"x")
        assert exc_info.value.provider == "s3"


# ── LSP compliance: all adapters honour the same contract ────────────────────


class TestLSPCompliance:
    """Verify that all adapters are interchangeable (Liskov Substitution)."""

    @pytest.fixture(params=["gcs", "azure"])
    def any_adapter(
        self, request: pytest.FixtureRequest, gcs_adapter: GCSStorageAdapter, azure_adapter: AzureStorageAdapter
    ) -> GCSStorageAdapter | AzureStorageAdapter:
        return gcs_adapter if request.param == "gcs" else azure_adapter

    def test_upload_download_roundtrip(self, any_adapter: GCSStorageAdapter | AzureStorageAdapter) -> None:
        data = b"LSP test payload"
        any_adapter.upload("lsp/test.bin", data)
        retrieved = any_adapter.download("lsp/test.bin")
        assert retrieved == data

    def test_list_returns_list(self, any_adapter: GCSStorageAdapter | AzureStorageAdapter) -> None:
        result = any_adapter.list_keys()
        assert isinstance(result, list)

    def test_missing_key_raises_storage_key_not_found(self, any_adapter: GCSStorageAdapter | AzureStorageAdapter) -> None:
        with pytest.raises(StorageKeyNotFoundError):
            any_adapter.download("never/uploaded.bin")
