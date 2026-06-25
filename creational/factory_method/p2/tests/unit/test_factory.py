"""Unit tests for the Storage Factory Method pattern."""
from __future__ import annotations

import pytest

from storage.domain.entities import FileNotFoundInStorageError
from storage.domain.interfaces import StorageClient, StorageFactory
from storage.infrastructure.creators import (
    GCSStorageClient,
    GCSStorageFactory,
    LocalStorageClient,
    LocalStorageFactory,
    PROVIDER_REGISTRY,
)


# ── Factory Method contract ────────────────────────────────────────────────────

class TestLocalStorageFactory:
    def test_create_returns_storage_client(self, local_factory: LocalStorageFactory) -> None:
        client = local_factory.create_client()
        assert isinstance(client, StorageClient)

    def test_provider_name(self, local_factory: LocalStorageFactory) -> None:
        assert local_factory.get_provider_name() == "Local"

    def test_upload_download_roundtrip(
        self, local_factory: LocalStorageFactory, sample_data: bytes
    ) -> None:
        client = local_factory.create_client()
        url = client.upload("test/file.txt", sample_data)
        assert url.startswith("file://")
        downloaded = client.download("test/file.txt")
        assert downloaded == sample_data

    def test_list_keys_after_upload(self, local_factory: LocalStorageFactory) -> None:
        client = local_factory.create_client()
        client.upload("a/1.txt", b"data1")
        client.upload("a/2.txt", b"data2")
        client.upload("b/3.txt", b"data3")
        keys = client.list_keys(prefix="a/")
        assert len(keys) == 2

    def test_delete_removes_file(self, local_factory: LocalStorageFactory) -> None:
        client = local_factory.create_client()
        client.upload("to_delete.txt", b"bye")
        client.delete("to_delete.txt")
        with pytest.raises(FileNotFoundInStorageError):
            client.download("to_delete.txt")

    def test_download_nonexistent_raises(self, local_factory: LocalStorageFactory) -> None:
        client = local_factory.create_client()
        with pytest.raises(FileNotFoundInStorageError):
            client.download("does_not_exist.txt")


class TestGCSStorageFactory:
    def test_create_returns_storage_client(self, gcs_factory: GCSStorageFactory) -> None:
        client = gcs_factory.create_client()
        assert isinstance(client, StorageClient)

    def test_provider_name(self, gcs_factory: GCSStorageFactory) -> None:
        assert gcs_factory.get_provider_name() == "GCS"

    def test_upload_returns_gs_url(
        self, gcs_factory: GCSStorageFactory, sample_data: bytes
    ) -> None:
        client = gcs_factory.create_client()
        url = client.upload("test.bin", sample_data)
        assert url.startswith("gs://")

    def test_download_roundtrip(
        self, gcs_factory: GCSStorageFactory, sample_data: bytes
    ) -> None:
        client = gcs_factory.create_client()
        client.upload("roundtrip.bin", sample_data)
        assert client.download("roundtrip.bin") == sample_data

    def test_delete(self, gcs_factory: GCSStorageFactory) -> None:
        client = gcs_factory.create_client()
        client.upload("del.txt", b"x")
        client.delete("del.txt")
        with pytest.raises(FileNotFoundInStorageError):
            client.download("del.txt")

    def test_list_keys_prefix_filter(self, gcs_factory: GCSStorageFactory) -> None:
        client = gcs_factory.create_client()
        client.upload("images/cat.png", b"cat")
        client.upload("images/dog.png", b"dog")
        client.upload("docs/readme.md", b"readme")
        images = client.list_keys("images/")
        assert len(images) == 2


# ── OCP — new provider without touching existing code ─────────────────────────

class TestProviderRegistry:
    def test_all_providers_registered(self) -> None:
        assert set(PROVIDER_REGISTRY.keys()) == {"s3", "gcs", "local"}

    def test_each_creates_valid_client_interface(
        self, gcs_factory: GCSStorageFactory, local_factory: LocalStorageFactory
    ) -> None:
        for factory in [gcs_factory, local_factory]:
            client = factory.create_client()
            assert isinstance(client, StorageClient)


# ── DIP — use case with custom factory ────────────────────────────────────────

class InMemoryStorageFactory(StorageFactory):
    """Test-double factory to verify DIP in use cases."""

    class _InMemoryClient:
        def __init__(self) -> None:
            self._store: dict[str, bytes] = {}

        def upload(self, key: str, data: bytes) -> str:
            self._store[key] = data
            return f"mem://{key}"

        def download(self, key: str) -> bytes:
            if key not in self._store:
                raise FileNotFoundInStorageError(key, "InMemory")
            return self._store[key]

        def delete(self, key: str) -> None:
            if key not in self._store:
                raise FileNotFoundInStorageError(key, "InMemory")
            del self._store[key]

        def list_keys(self, prefix: str = "") -> list[str]:
            return [k for k in self._store if k.startswith(prefix)]

    def create_client(self) -> StorageClient:
        return self._InMemoryClient()  # type: ignore[return-value]

    def get_provider_name(self) -> str:
        return "InMemory"


class TestDependencyInversion:
    def test_upload_use_case_accepts_any_factory(self, sample_data: bytes) -> None:
        from storage.application.use_cases import UploadFileUseCase

        factory = InMemoryStorageFactory()
        use_case = UploadFileUseCase(factory)
        result = use_case.execute("test.bin", sample_data)
        assert result.url == "mem://test.bin"
        assert result.size_bytes == len(sample_data)
