"""Unit tests for ListObjectsPageUseCase and SummarizeBucketUseCase."""

from __future__ import annotations

from s3_iterator.application.use_cases import (
    ListObjectsPageUseCase,
    SummarizeBucketUseCase,
)
from tests.unit.test_object_iterator import FakeS3ObjectSource


def test_list_objects_page_returns_requested_page() -> None:
    source = FakeS3ObjectSource(total=5)
    use_case = ListObjectsPageUseCase(source)

    page = use_case.execute(continuation_token=None, limit=2)

    assert [obj.key for obj in page.items] == ["file-000.txt", "file-001.txt"]
    assert page.next_token == "2"


def test_summarize_bucket_counts_and_sums_size_across_pages() -> None:
    source = FakeS3ObjectSource(total=10)
    use_case = SummarizeBucketUseCase(source, page_size=3)

    summary = use_case.execute()

    assert summary.object_count == 10
    assert summary.total_size_bytes == sum(range(10))


def test_summarize_empty_bucket_returns_zeroes() -> None:
    source = FakeS3ObjectSource(total=0)
    use_case = SummarizeBucketUseCase(source)

    summary = use_case.execute()

    assert summary.object_count == 0
    assert summary.total_size_bytes == 0
