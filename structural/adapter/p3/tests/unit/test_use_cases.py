"""Unit tests for cloud_adapter application use cases."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from cloud_adapter.application.use_cases import (
    DeleteFileUseCase,
    DownloadFileUseCase,
    ListFilesUseCase,
    UploadFileUseCase,
)
from cloud_adapter.domain.entities import UploadResult
from cloud_adapter.domain.interfaces import CloudStorage


@pytest.fixture()
def mock_storage() -> MagicMock:
    """A mock that passes runtime isinstance checks for CloudStorage."""
    mock = MagicMock(spec=CloudStorage)
    return mock


class TestUploadFileUseCase:
    def test_returns_upload_result(self, mock_storage: MagicMock) -> None:
        mock_storage.upload.return_value = "https://example.com/key.txt"
        result = UploadFileUseCase(mock_storage, "s3").execute("key.txt", b"data")
        assert isinstance(result, UploadResult)
        assert result.key == "key.txt"
        assert result.provider == "s3"
        assert result.size == 4
        assert result.url == "https://example.com/key.txt"

    def test_delegates_to_storage_upload(self, mock_storage: MagicMock) -> None:
        mock_storage.upload.return_value = "https://example.com/k"
        UploadFileUseCase(mock_storage, "gcs").execute("k", b"bytes")
        mock_storage.upload.assert_called_once_with("k", b"bytes")


class TestDownloadFileUseCase:
    def test_returns_bytes_from_storage(self, mock_storage: MagicMock) -> None:
        mock_storage.download.return_value = b"content"
        result = DownloadFileUseCase(mock_storage).execute("file.txt")
        assert result == b"content"
        mock_storage.download.assert_called_once_with("file.txt")


class TestDeleteFileUseCase:
    def test_calls_storage_delete(self, mock_storage: MagicMock) -> None:
        DeleteFileUseCase(mock_storage).execute("old.bin")
        mock_storage.delete.assert_called_once_with("old.bin")


class TestListFilesUseCase:
    def test_returns_key_list(self, mock_storage: MagicMock) -> None:
        mock_storage.list_keys.return_value = ["a.txt", "b.txt"]
        result = ListFilesUseCase(mock_storage).execute(prefix="")
        assert result == ["a.txt", "b.txt"]

    def test_passes_prefix_to_storage(self, mock_storage: MagicMock) -> None:
        mock_storage.list_keys.return_value = []
        ListFilesUseCase(mock_storage).execute(prefix="docs/")
        mock_storage.list_keys.assert_called_once_with("docs/")
