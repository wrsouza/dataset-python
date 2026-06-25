"""Unit tests for Cloud Storage Factory use cases.

Uses GCS and Azure fakes — no external services required.
Verifies the Abstract Factory pattern and SOLID principles.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from cloud_storage.application.use_cases import (
    DeleteFileUseCase,
    DownloadFileUseCase,
    GetMetadataUseCase,
    GetSignedUrlUseCase,
    UploadFileUseCase,
)
from cloud_storage.domain.entities import (
    ObjectNotFoundError,
    SignedUrlResult,
    UploadResult,
)
from cloud_storage.infrastructure.factories import (
    AzureStorageFactory,
    GCSStorageFactory,
    build_factory_for_provider,
)

SAMPLE_DATA = b"hello, abstract factory"
SAMPLE_KEY = "test/sample.txt"
SAMPLE_CONTENT_TYPE = "text/plain"


class TestUploadFileUseCase:
    def test_upload_returns_upload_result(
        self, gcs_factory: GCSStorageFactory
    ) -> None:
        use_case = UploadFileUseCase(factory=gcs_factory)
        result = use_case.execute(SAMPLE_KEY, SAMPLE_DATA, SAMPLE_CONTENT_TYPE)
        assert isinstance(result, UploadResult)
        assert result.key == SAMPLE_KEY
        assert result.size_bytes == len(SAMPLE_DATA)

    def test_upload_records_provider_name(
        self, gcs_factory: GCSStorageFactory
    ) -> None:
        result = UploadFileUseCase(factory=gcs_factory).execute(
            SAMPLE_KEY, SAMPLE_DATA, SAMPLE_CONTENT_TYPE
        )
        assert result.provider == "gcs"

    def test_upload_azure_records_azure_provider(
        self, azure_factory: AzureStorageFactory
    ) -> None:
        result = UploadFileUseCase(factory=azure_factory).execute(
            SAMPLE_KEY, SAMPLE_DATA, SAMPLE_CONTENT_TYPE
        )
        assert result.provider == "azure"

    def test_upload_result_to_dict(
        self, gcs_factory: GCSStorageFactory
    ) -> None:
        result = UploadFileUseCase(factory=gcs_factory).execute(
            SAMPLE_KEY, SAMPLE_DATA, SAMPLE_CONTENT_TYPE
        )
        d = result.to_dict()
        assert d["key"] == SAMPLE_KEY
        assert "object_identifier" in d


class TestDownloadFileUseCase:
    def test_download_returns_uploaded_bytes(
        self, gcs_factory: GCSStorageFactory
    ) -> None:
        UploadFileUseCase(factory=gcs_factory).execute(
            SAMPLE_KEY, SAMPLE_DATA, SAMPLE_CONTENT_TYPE
        )
        downloaded = DownloadFileUseCase(factory=gcs_factory).execute(SAMPLE_KEY)
        assert downloaded == SAMPLE_DATA

    def test_download_missing_key_raises_object_not_found(
        self, azure_factory: AzureStorageFactory
    ) -> None:
        with pytest.raises(ObjectNotFoundError):
            DownloadFileUseCase(factory=azure_factory).execute("nonexistent/key")


class TestDeleteFileUseCase:
    def test_delete_removes_object(
        self, gcs_factory: GCSStorageFactory
    ) -> None:
        UploadFileUseCase(factory=gcs_factory).execute(
            SAMPLE_KEY, SAMPLE_DATA, SAMPLE_CONTENT_TYPE
        )
        DeleteFileUseCase(factory=gcs_factory).execute(SAMPLE_KEY)
        with pytest.raises(ObjectNotFoundError):
            DownloadFileUseCase(factory=gcs_factory).execute(SAMPLE_KEY)

    def test_delete_nonexistent_key_does_not_raise(
        self, azure_factory: AzureStorageFactory
    ) -> None:
        # Azure fake silently ignores delete of nonexistent keys
        DeleteFileUseCase(factory=azure_factory).execute("ghost/key")


class TestGetSignedUrlUseCase:
    def test_returns_signed_url_result(
        self, gcs_factory: GCSStorageFactory
    ) -> None:
        result = GetSignedUrlUseCase(factory=gcs_factory).execute(SAMPLE_KEY)
        assert isinstance(result, SignedUrlResult)
        assert result.key == SAMPLE_KEY
        assert result.signed_url.startswith("https://")

    def test_expiry_propagated_to_result(
        self, azure_factory: AzureStorageFactory
    ) -> None:
        result = GetSignedUrlUseCase(factory=azure_factory).execute(
            SAMPLE_KEY, expires_in_seconds=7200
        )
        assert result.expires_in_seconds == 7200

    def test_gcs_url_contains_expiry_param(
        self, gcs_factory: GCSStorageFactory
    ) -> None:
        result = GetSignedUrlUseCase(factory=gcs_factory).execute(
            SAMPLE_KEY, expires_in_seconds=300
        )
        assert "Expires" in result.signed_url or "X-Goog-Expires" in result.signed_url

    def test_dip_same_use_case_works_with_all_providers(self) -> None:
        """DIP: GetSignedUrlUseCase is unchanged regardless of provider."""
        for factory in [GCSStorageFactory(), AzureStorageFactory()]:
            result = GetSignedUrlUseCase(factory=factory).execute(SAMPLE_KEY)
            assert result.provider == factory.get_provider_name()


class TestGetMetadataUseCase:
    def test_returns_metadata_after_upload(
        self, gcs_factory: GCSStorageFactory
    ) -> None:
        UploadFileUseCase(factory=gcs_factory).execute(
            SAMPLE_KEY, SAMPLE_DATA, SAMPLE_CONTENT_TYPE
        )
        meta = GetMetadataUseCase(factory=gcs_factory).execute(SAMPLE_KEY)
        assert meta.key == SAMPLE_KEY
        assert "content_length" in meta.metadata

    def test_metadata_missing_key_raises_not_found(
        self, azure_factory: AzureStorageFactory
    ) -> None:
        with pytest.raises(ObjectNotFoundError):
            GetMetadataUseCase(factory=azure_factory).execute("missing")


class TestBuildFactoryForProvider:
    @pytest.mark.parametrize("provider", ["gcs", "azure"])
    def test_returns_correct_provider(self, provider: str) -> None:
        factory = build_factory_for_provider(provider)
        assert factory.get_provider_name() == provider

    def test_unknown_provider_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Unknown provider"):
            build_factory_for_provider("dropbox")

    def test_ocp_gcs_and_azure_are_independent_families(self) -> None:
        """OCP: each factory's products are independent — changing one does not affect others."""
        gcs = build_factory_for_provider("gcs")
        azure = build_factory_for_provider("azure")
        gcs.create_storage_client().upload(SAMPLE_KEY, SAMPLE_DATA, SAMPLE_CONTENT_TYPE)
        # Azure should not have the GCS-uploaded object
        with pytest.raises(ObjectNotFoundError):
            azure.create_storage_client().download(SAMPLE_KEY)
