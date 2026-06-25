"""Unit tests for application use cases (Composite pattern orchestration)."""

from __future__ import annotations

import pytest

from filesystem.application.use_cases import (
    CalculateTotalSizeUseCase,
    CreateDirectoryUseCase,
    DeleteNodeUseCase,
    GetTreeUseCase,
    ListContentsUseCase,
    UploadFileUseCase,
)
from filesystem.domain.exceptions import FSNodeNotFoundError
from filesystem.infrastructure.s3_client import S3StorageClient


class TestUploadFileUseCase:
    def test_execute_stores_file_in_s3(self, storage: S3StorageClient) -> None:
        use_case = UploadFileUseCase(storage)

        use_case.execute("a/b.txt", b"hello world", "text/plain")

        node = storage.get_node("a/b.txt")
        assert node.get_size() == len(b"hello world")


class TestCreateDirectoryUseCase:
    def test_execute_creates_folder_marker(self, storage: S3StorageClient) -> None:
        use_case = CreateDirectoryUseCase(storage)

        use_case.execute("photos")

        node = storage.get_node("photos")
        assert node.to_dict()["type"] == "folder"


class TestGetTreeUseCase:
    def test_execute_returns_file_dict(self, storage: S3StorageClient) -> None:
        UploadFileUseCase(storage).execute("notes.txt", b"hi", "text/plain")

        result = GetTreeUseCase(storage).execute("notes.txt")

        assert result["type"] == "file"
        assert result["path"] == "notes.txt"

    def test_execute_returns_folder_tree(self, storage: S3StorageClient) -> None:
        CreateDirectoryUseCase(storage).execute("docs")
        UploadFileUseCase(storage).execute("docs/a.txt", b"1", "text/plain")

        result = GetTreeUseCase(storage).execute("docs")

        assert result["type"] == "folder"
        assert result["children"][0]["path"] == "docs/a.txt"

    def test_execute_raises_when_path_missing(self, storage: S3StorageClient) -> None:
        with pytest.raises(FSNodeNotFoundError):
            GetTreeUseCase(storage).execute("missing/path")


class TestCalculateTotalSizeUseCase:
    def test_execute_sums_nested_files(self, storage: S3StorageClient) -> None:
        UploadFileUseCase(storage).execute("docs/a.txt", b"123", "text/plain")
        UploadFileUseCase(storage).execute("docs/b.txt", b"12345", "text/plain")

        total = CalculateTotalSizeUseCase(storage).execute("docs")

        assert total == 8

    def test_execute_single_file_returns_its_size(
        self, storage: S3StorageClient
    ) -> None:
        UploadFileUseCase(storage).execute("a.txt", b"abcdef", "text/plain")

        total = CalculateTotalSizeUseCase(storage).execute("a.txt")

        assert total == 6


class TestListContentsUseCase:
    def test_execute_lists_all_descendant_files(self, storage: S3StorageClient) -> None:
        UploadFileUseCase(storage).execute("docs/a.txt", b"1", "text/plain")
        UploadFileUseCase(storage).execute("docs/sub/b.txt", b"22", "text/plain")

        contents = ListContentsUseCase(storage).execute("docs")

        assert {c["path"] for c in contents} == {"docs/a.txt", "docs/sub/b.txt"}


class TestDeleteNodeUseCase:
    def test_execute_deletes_file(self, storage: S3StorageClient) -> None:
        UploadFileUseCase(storage).execute("a.txt", b"1", "text/plain")

        DeleteNodeUseCase(storage).execute("a.txt")

        with pytest.raises(FSNodeNotFoundError):
            GetTreeUseCase(storage).execute("a.txt")

    def test_execute_deletes_folder_and_children(
        self, storage: S3StorageClient
    ) -> None:
        CreateDirectoryUseCase(storage).execute("docs")
        UploadFileUseCase(storage).execute("docs/a.txt", b"1", "text/plain")

        DeleteNodeUseCase(storage).execute("docs")

        with pytest.raises(FSNodeNotFoundError):
            GetTreeUseCase(storage).execute("docs")

    def test_execute_raises_when_path_missing(self, storage: S3StorageClient) -> None:
        with pytest.raises(FSNodeNotFoundError):
            DeleteNodeUseCase(storage).execute("ghost")
