"""Unit tests for domain value objects."""

from __future__ import annotations

from src.remote_files.domain.entities import CacheStats, FileMetadata


class TestFileMetadata:
    def test_stores_key_size_and_exists(self) -> None:
        metadata = FileMetadata(key="a.txt", size_bytes=10, exists=True)
        assert metadata.key == "a.txt"
        assert metadata.size_bytes == 10
        assert metadata.exists is True

    def test_is_frozen(self) -> None:
        metadata = FileMetadata(key="a.txt", size_bytes=10, exists=True)
        try:
            metadata.size_bytes = 20  # type: ignore[misc]
        except AttributeError:
            pass
        else:
            raise AssertionError("FileMetadata should be immutable")


class TestCacheStats:
    def test_total_reads_sums_hits_and_misses(self) -> None:
        stats = CacheStats(cache_hits=3, cache_misses=2, bytes_saved=300)
        assert stats.total_reads == 5

    def test_hit_ratio_computed_correctly(self) -> None:
        stats = CacheStats(cache_hits=3, cache_misses=1, bytes_saved=300)
        assert stats.hit_ratio == 0.75

    def test_hit_ratio_is_zero_when_no_reads(self) -> None:
        stats = CacheStats(cache_hits=0, cache_misses=0, bytes_saved=0)
        assert stats.hit_ratio == 0.0
