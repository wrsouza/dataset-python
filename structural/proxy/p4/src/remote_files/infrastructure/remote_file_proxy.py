"""Proxy: RemoteFileProxy, a Virtual + Caching Proxy over a FileResource.

RemoteFileProxy implements the same FileResource interface as RealS3File
(LSP: callers cannot tell the difference) but adds two behaviours the
RealSubject deliberately does not have:

1. Virtual/lazy loading: the real download (a network call) is deferred
   until the first .read(). Constructing the proxy never touches S3.
2. Caching: once content has been downloaded, subsequent .read() calls
   return the cached bytes with zero extra network calls.

The proxy depends only on the FileResource Protocol (DIP), so it works in
front of any RealSubject, real or fake, without modification (OCP).
"""

from __future__ import annotations

from src.remote_files.domain.entities import CacheStats
from src.remote_files.domain.exceptions import CacheEvictionError
from src.remote_files.domain.interfaces import FileResource


class RemoteFileProxy:
    """Lazily loads and caches the content of a remote FileResource."""

    def __init__(self, real_subject: FileResource) -> None:
        self._real_subject = real_subject
        self._cached_content: bytes | None = None
        self._cache_hits = 0
        self._cache_misses = 0

    @property
    def key(self) -> str:
        """Return the object key, delegating to the real subject (cheap)."""
        return self._real_subject.key

    @property
    def size(self) -> int:
        """Return the file size, delegating to the real subject (cheap)."""
        return self._real_subject.size

    def exists(self) -> bool:
        """Check existence without downloading content."""
        return self._real_subject.exists()

    def read(self) -> bytes:
        """Return file content, downloading once and caching for later reads."""
        if self._cached_content is not None:
            self._cache_hits += 1
            return self._cached_content

        content = self._real_subject.read()
        self._cached_content = content
        self._cache_misses += 1
        return content

    def invalidate(self) -> None:
        """Drop the cached content, forcing the next read() to hit S3 again."""
        if self._cached_content is None:
            raise CacheEvictionError(self.key)
        self._cached_content = None

    def is_cached(self) -> bool:
        """Return whether content is currently held in the local cache."""
        return self._cached_content is not None

    def cache_stats(self) -> CacheStats:
        """Return aggregated cache hit/miss statistics for this proxy."""
        bytes_saved = 0
        if self._cache_hits and self._cached_content is not None:
            bytes_saved = self._cache_hits * len(self._cached_content)
        return CacheStats(
            cache_hits=self._cache_hits,
            cache_misses=self._cache_misses,
            bytes_saved=bytes_saved,
        )
