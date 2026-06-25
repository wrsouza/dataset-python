"""Application use cases for file storage — depend only on abstractions (DIP)."""
from __future__ import annotations

from storage.domain.entities import FileMetadata, UploadResult
from storage.domain.interfaces import StorageFactory


class UploadFileUseCase:
    """Upload a file through the injected storage factory."""

    def __init__(self, factory: StorageFactory) -> None:
        self._factory = factory

    def execute(self, key: str, data: bytes) -> UploadResult:
        client = self._factory.create_client()
        url = client.upload(key, data)
        return UploadResult(
            key=key,
            provider=self._factory.get_provider_name(),
            url=url,
            size_bytes=len(data),
        )


class DownloadFileUseCase:
    """Download a file through the injected storage factory."""

    def __init__(self, factory: StorageFactory) -> None:
        self._factory = factory

    def execute(self, key: str) -> bytes:
        client = self._factory.create_client()
        return client.download(key)


class DeleteFileUseCase:
    """Delete a file through the injected storage factory."""

    def __init__(self, factory: StorageFactory) -> None:
        self._factory = factory

    def execute(self, key: str) -> None:
        client = self._factory.create_client()
        client.delete(key)


class ListFilesUseCase:
    """List files in the storage backend for the given provider."""

    def __init__(self, factory: StorageFactory) -> None:
        self._factory = factory

    def execute(self, prefix: str = "") -> list[str]:
        client = self._factory.create_client()
        return client.list_keys(prefix)
