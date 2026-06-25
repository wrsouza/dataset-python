"""Application use cases for cloud_adapter.

Use cases depend only on the CloudStorage Protocol (DIP).
No SDK, no Django ORM — pure application logic.
"""

from __future__ import annotations

from cloud_adapter.domain.entities import UploadResult
from cloud_adapter.domain.interfaces import CloudStorage


class UploadFileUseCase:
    """Upload raw bytes via the injected storage adapter."""

    def __init__(self, storage: CloudStorage, provider: str) -> None:
        self._storage = storage
        self._provider = provider

    def execute(self, key: str, data: bytes) -> UploadResult:
        url = self._storage.upload(key, data)
        return UploadResult(
            key=key,
            provider=self._provider,
            url=url,
            size=len(data),
        )


class DownloadFileUseCase:
    """Download raw bytes via the injected storage adapter."""

    def __init__(self, storage: CloudStorage) -> None:
        self._storage = storage

    def execute(self, key: str) -> bytes:
        return self._storage.download(key)


class DeleteFileUseCase:
    """Delete an object via the injected storage adapter."""

    def __init__(self, storage: CloudStorage) -> None:
        self._storage = storage

    def execute(self, key: str) -> None:
        self._storage.delete(key)


class ListFilesUseCase:
    """List keys via the injected storage adapter."""

    def __init__(self, storage: CloudStorage) -> None:
        self._storage = storage

    def execute(self, prefix: str = "") -> list[str]:
        return self._storage.list_keys(prefix)
