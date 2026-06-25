"""Unit tests for RemoteFileProxy -- the heart of this project.

These tests prove the central educational claim: the real download only
happens on the first read(); every subsequent read() is served from the
local cache without any extra call to the RealSubject, verified through the
FakeFileResource's call counters (no mocking framework needed).
"""

from __future__ import annotations

import pytest

from src.remote_files.domain.exceptions import CacheEvictionError
from src.remote_files.infrastructure.remote_file_proxy import RemoteFileProxy
from tests.conftest import TEST_CONTENT, FakeFileResource


@pytest.fixture
def proxy(fake_resource: FakeFileResource) -> RemoteFileProxy:
    return RemoteFileProxy(real_subject=fake_resource)


class TestLazyLoading:
    def test_constructing_proxy_does_not_touch_real_subject(
        self, fake_resource: FakeFileResource
    ) -> None:
        RemoteFileProxy(real_subject=fake_resource)
        assert fake_resource.read_calls == 0

    def test_first_read_delegates_to_real_subject(
        self, proxy: RemoteFileProxy, fake_resource: FakeFileResource
    ) -> None:
        content = proxy.read()
        assert content == TEST_CONTENT
        assert fake_resource.read_calls == 1


class TestCaching:
    def test_second_read_does_not_call_real_subject_again(
        self, proxy: RemoteFileProxy, fake_resource: FakeFileResource
    ) -> None:
        proxy.read()
        proxy.read()
        proxy.read()
        assert fake_resource.read_calls == 1

    def test_is_cached_reflects_state(self, proxy: RemoteFileProxy) -> None:
        assert proxy.is_cached() is False
        proxy.read()
        assert proxy.is_cached() is True

    def test_invalidate_clears_cache_and_forces_new_download(
        self, proxy: RemoteFileProxy, fake_resource: FakeFileResource
    ) -> None:
        proxy.read()
        proxy.invalidate()
        assert proxy.is_cached() is False
        proxy.read()
        assert fake_resource.read_calls == 2

    def test_invalidate_without_cache_raises(self, proxy: RemoteFileProxy) -> None:
        with pytest.raises(CacheEvictionError):
            proxy.invalidate()


class TestCacheStats:
    def test_tracks_hits_and_misses(self, proxy: RemoteFileProxy) -> None:
        proxy.read()
        proxy.read()
        proxy.read()
        stats = proxy.cache_stats()
        assert stats.cache_misses == 1
        assert stats.cache_hits == 2
        assert stats.total_reads == 3

    def test_bytes_saved_accounts_for_cache_hits_only(
        self, proxy: RemoteFileProxy
    ) -> None:
        proxy.read()
        proxy.read()
        stats = proxy.cache_stats()
        assert stats.bytes_saved == len(TEST_CONTENT) * 1

    def test_no_reads_yields_zero_stats(self, proxy: RemoteFileProxy) -> None:
        stats = proxy.cache_stats()
        assert stats.cache_hits == 0
        assert stats.cache_misses == 0
        assert stats.bytes_saved == 0


class TestDelegatedAccessors:
    def test_key_delegates_to_real_subject(
        self, proxy: RemoteFileProxy, fake_resource: FakeFileResource
    ) -> None:
        assert proxy.key == fake_resource.key

    def test_size_delegates_to_real_subject(
        self, proxy: RemoteFileProxy, fake_resource: FakeFileResource
    ) -> None:
        assert proxy.size == len(TEST_CONTENT)

    def test_exists_delegates_to_real_subject(
        self, proxy: RemoteFileProxy, fake_resource: FakeFileResource
    ) -> None:
        assert proxy.exists() is True
        assert fake_resource.exists_calls == 1

    def test_exists_does_not_populate_cache(self, proxy: RemoteFileProxy) -> None:
        proxy.exists()
        assert proxy.is_cached() is False
