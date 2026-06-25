"""Value objects shared by the application and infrastructure layers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FileMetadata:
    """Lightweight metadata about a remote file, obtainable without downloading it."""

    key: str
    size_bytes: int
    exists: bool


@dataclass(frozen=True)
class CacheStats:
    """Aggregated cache statistics exposed by a RemoteFileProxy.

    cache_hits: number of read() calls served from the local cache.
    cache_misses: number of read() calls that triggered a real download.
    bytes_saved: bytes that did NOT need to travel over the network thanks
        to the cache (i.e. the size of every cache-hit response).
    """

    cache_hits: int
    cache_misses: int
    bytes_saved: int

    @property
    def total_reads(self) -> int:
        """Total number of read() calls observed so far."""
        return self.cache_hits + self.cache_misses

    @property
    def hit_ratio(self) -> float:
        """Fraction of reads served from cache, in the [0.0, 1.0] range."""
        if self.total_reads == 0:
            return 0.0
        return self.cache_hits / self.total_reads
