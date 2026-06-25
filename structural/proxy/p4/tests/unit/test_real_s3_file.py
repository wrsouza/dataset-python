"""Unit tests for RealS3File (the RealSubject), using moto for the happy
path and a manual ClientError for unexpected-failure paths."""

from __future__ import annotations

import pytest
from botocore.exceptions import ClientError

from src.remote_files.domain.exceptions import (
    FileNotFoundInRemoteError,
    RemoteStorageError,
)
from src.remote_files.infrastructure.real_s3_file import RealS3File
from tests.conftest import TEST_BUCKET, TEST_CONTENT, TEST_KEY


def _client_error(operation: str, code: str = "500") -> ClientError:
    return ClientError(
        error_response={"Error": {"Code": code, "Message": "boom"}},
        operation_name=operation,
    )


class TestRead:
    def test_downloads_content_from_s3(self, real_s3_file: RealS3File) -> None:
        assert real_s3_file.read() == TEST_CONTENT

    def test_raises_not_found_for_missing_key(self, populated_moto_s3: object) -> None:
        missing = RealS3File(
            bucket=TEST_BUCKET, key="missing.txt", s3_client=populated_moto_s3
        )
        with pytest.raises(FileNotFoundInRemoteError) as exc_info:
            missing.read()
        assert exc_info.value.key == "missing.txt"

    def test_raises_remote_storage_error_on_unexpected_failure(self) -> None:
        class _BrokenClient:
            def get_object(self, **_: object) -> object:
                raise _client_error("GetObject")

        broken = RealS3File(bucket=TEST_BUCKET, key=TEST_KEY, s3_client=_BrokenClient())
        with pytest.raises(RemoteStorageError) as exc_info:
            broken.read()
        assert exc_info.value.bucket == TEST_BUCKET


class TestExists:
    def test_true_for_existing_object(self, real_s3_file: RealS3File) -> None:
        assert real_s3_file.exists() is True

    def test_false_for_missing_object(self, populated_moto_s3: object) -> None:
        missing = RealS3File(
            bucket=TEST_BUCKET, key="missing.txt", s3_client=populated_moto_s3
        )
        assert missing.exists() is False

    def test_propagates_unexpected_failure(self) -> None:
        class _BrokenClient:
            def head_object(self, **_: object) -> object:
                raise _client_error("HeadObject")

        broken = RealS3File(bucket=TEST_BUCKET, key=TEST_KEY, s3_client=_BrokenClient())
        with pytest.raises(RemoteStorageError):
            broken.exists()


class TestSize:
    def test_returns_content_length(self, real_s3_file: RealS3File) -> None:
        assert real_s3_file.size == len(TEST_CONTENT)

    def test_raises_not_found_for_missing_key(self, populated_moto_s3: object) -> None:
        missing = RealS3File(
            bucket=TEST_BUCKET, key="missing.txt", s3_client=populated_moto_s3
        )
        with pytest.raises(FileNotFoundInRemoteError):
            _ = missing.size


class TestKeyProperty:
    def test_returns_configured_key(self, real_s3_file: RealS3File) -> None:
        assert real_s3_file.key == TEST_KEY
