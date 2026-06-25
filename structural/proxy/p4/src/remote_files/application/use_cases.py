"""Use cases orchestrating access to a FileResource (proxy or real subject).

Every use case here depends only on the FileResource Protocol (DIP) -- none
of them import RealS3File or RemoteFileProxy directly, nor boto3. The CLI
wires up the concrete instances and injects them.
"""

from __future__ import annotations

from src.remote_files.domain.entities import CacheStats, FileMetadata
from src.remote_files.domain.interfaces import FileResource
from src.remote_files.infrastructure.remote_file_proxy import RemoteFileProxy


class ReadFileUseCase:
    """Read the content of a remote file through the proxy (lazy + cached)."""

    def __init__(self, resource: FileResource) -> None:
        self._resource = resource

    def execute(self) -> bytes:
        """Return the file content, triggering a download only if needed."""
        return self._resource.read()


class CheckFileExistsUseCase:
    """Check whether a remote file exists without downloading its content."""

    def __init__(self, resource: FileResource) -> None:
        self._resource = resource

    def execute(self) -> FileMetadata:
        """Return metadata (key, size, exists) using only HEAD-style calls."""
        exists = self._resource.exists()
        size = self._resource.size if exists else 0
        return FileMetadata(key=self._resource.key, size_bytes=size, exists=exists)


class GetCacheStatsUseCase:
    """Report cache hit/miss statistics gathered by a RemoteFileProxy."""

    def __init__(self, proxy: RemoteFileProxy) -> None:
        self._proxy = proxy

    def execute(self) -> CacheStats:
        """Return the current cache statistics snapshot."""
        return self._proxy.cache_stats()
