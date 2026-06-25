"""Unit tests for S3StorageClient (infrastructure adapter), mocked via moto."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from filesystem.domain.entities import Directory, File
from filesystem.domain.exceptions import FSNodeNotFoundError, FSStorageError
from filesystem.infrastructure.s3_client import S3StorageClient


def _client_error(operation: str, code: str = "500") -> ClientError:
    return ClientError(
        error_response={"Error": {"Code": code, "Message": "boom"}},
        operation_name=operation,
    )


class TestEnsureBucket:
    def test_constructor_creates_bucket_if_missing(self, moto_s3: object) -> None:
        client = S3StorageClient(s3_client=moto_s3, bucket="brand-new-bucket")

        # No exception means head_bucket succeeded after creation.
        client._s3.head_bucket(Bucket="brand-new-bucket")  # noqa: SLF001

    def test_constructor_reuses_existing_bucket(self, moto_s3: object) -> None:
        moto_s3.create_bucket(Bucket="already-exists")  # type: ignore[attr-defined]

        S3StorageClient(s3_client=moto_s3, bucket="already-exists")  # should not raise


class TestGetNode:
    def test_returns_file_for_exact_key(self, storage: S3StorageClient) -> None:
        storage.put_file("a.txt", b"hello", "text/plain")

        node = storage.get_node("a.txt")

        assert isinstance(node, File)
        assert node.get_size() == len(b"hello")

    def test_returns_directory_for_prefix_with_children(
        self, storage: S3StorageClient
    ) -> None:
        storage.put_file("docs/a.txt", b"1", "text/plain")

        node = storage.get_node("docs")

        assert isinstance(node, Directory)

    def test_raises_not_found_for_missing_path(self, storage: S3StorageClient) -> None:
        with pytest.raises(FSNodeNotFoundError):
            storage.get_node("nowhere")

    def test_raises_storage_error_on_unexpected_head_object_failure(self) -> None:
        fake_s3 = MagicMock()
        fake_s3.head_bucket.return_value = {}
        fake_s3.head_object.side_effect = _client_error("HeadObject")
        client = S3StorageClient(s3_client=fake_s3, bucket="any-bucket")

        with pytest.raises(FSStorageError):
            client.get_node("broken.txt")


class TestListDirectChildren:
    def test_lists_files_and_subfolders_non_recursively(
        self, storage: S3StorageClient
    ) -> None:
        storage.put_file("docs/a.txt", b"1", "text/plain")
        storage.put_folder("docs/sub")
        storage.put_file("docs/sub/b.txt", b"22", "text/plain")

        children = storage.list_direct_children("docs/")

        paths = {c.get_path() for c in children}
        assert "docs/a.txt" in paths
        assert any(p.startswith("docs/sub") for p in paths)
        assert "docs/sub/b.txt" not in paths

    def test_skips_folder_marker_itself(self, storage: S3StorageClient) -> None:
        storage.put_folder("docs")
        storage.put_file("docs/a.txt", b"1", "text/plain")

        children = storage.list_direct_children("docs/")

        assert "docs/" not in {c.get_path() for c in children}


class TestPutAndDelete:
    def test_put_file_stores_content_type(self, storage: S3StorageClient) -> None:
        storage.put_file("img.png", b"\x89PNG", "image/png")

        head = storage._s3.head_object(
            Bucket=storage._bucket, Key="img.png"
        )  # noqa: SLF001

        assert head["ContentType"] == "image/png"

    def test_put_folder_creates_empty_marker(self, storage: S3StorageClient) -> None:
        storage.put_folder("empty-dir")

        head = storage._s3.head_object(  # noqa: SLF001
            Bucket=storage._bucket, Key="empty-dir/"
        )

        assert head["ContentLength"] == 0

    def test_delete_object_removes_key(self, storage: S3StorageClient) -> None:
        storage.put_file("a.txt", b"1", "text/plain")

        storage.delete_object("a.txt")

        with pytest.raises(FSNodeNotFoundError):
            storage.get_node("a.txt")

    def test_delete_object_is_idempotent_for_missing_key(
        self, storage: S3StorageClient
    ) -> None:
        storage.delete_object("never-existed.txt")  # should not raise

    def test_delete_object_raises_storage_error_on_unexpected_failure(self) -> None:
        fake_s3 = MagicMock()
        fake_s3.head_bucket.return_value = {}
        fake_s3.delete_object.side_effect = _client_error("DeleteObject")
        client = S3StorageClient(s3_client=fake_s3, bucket="any-bucket")

        with pytest.raises(FSStorageError):
            client.delete_object("broken.txt")
