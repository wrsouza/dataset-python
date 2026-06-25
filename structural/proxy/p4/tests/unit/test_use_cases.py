"""Unit tests for application use cases, exercised against the Fake double."""

from __future__ import annotations

from src.remote_files.application.use_cases import (
    CheckFileExistsUseCase,
    GetCacheStatsUseCase,
    ReadFileUseCase,
)
from src.remote_files.infrastructure.remote_file_proxy import RemoteFileProxy
from tests.conftest import TEST_CONTENT, TEST_KEY, FakeFileResource


class TestReadFileUseCase:
    def test_returns_content_from_resource(
        self, fake_resource: FakeFileResource
    ) -> None:
        result = ReadFileUseCase(resource=fake_resource).execute()
        assert result == TEST_CONTENT


class TestCheckFileExistsUseCase:
    def test_existing_file_reports_size(self, fake_resource: FakeFileResource) -> None:
        metadata = CheckFileExistsUseCase(resource=fake_resource).execute()
        assert metadata.exists is True
        assert metadata.key == TEST_KEY
        assert metadata.size_bytes == len(TEST_CONTENT)

    def test_missing_file_reports_zero_size(self) -> None:
        missing = FakeFileResource(key="ghost.txt", content=b"", exists=False)
        metadata = CheckFileExistsUseCase(resource=missing).execute()
        assert metadata.exists is False
        assert metadata.size_bytes == 0

    def test_does_not_call_read(self, fake_resource: FakeFileResource) -> None:
        CheckFileExistsUseCase(resource=fake_resource).execute()
        assert fake_resource.read_calls == 0


class TestGetCacheStatsUseCase:
    def test_reports_stats_from_proxy(self, fake_resource: FakeFileResource) -> None:
        proxy = RemoteFileProxy(real_subject=fake_resource)
        proxy.read()
        proxy.read()
        stats = GetCacheStatsUseCase(proxy=proxy).execute()
        assert stats.cache_misses == 1
        assert stats.cache_hits == 1
