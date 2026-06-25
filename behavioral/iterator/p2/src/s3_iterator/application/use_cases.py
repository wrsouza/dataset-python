"""Use cases orchestrating paginated listing and full-bucket aggregation."""

from __future__ import annotations

from s3_iterator.domain.entities import BucketSummary, ObjectsPage
from s3_iterator.domain.interfaces import S3ObjectSource
from s3_iterator.infrastructure.object_iterator import S3KeyIterator


class ListObjectsPageUseCase:
    """Returns a single page of objects — the typical REST pagination request."""

    def __init__(self, source: S3ObjectSource) -> None:
        self._source = source

    def execute(self, continuation_token: str | None, limit: int) -> ObjectsPage:
        items, next_token = self._source.fetch_page(continuation_token, limit)
        return ObjectsPage(items=items, next_token=next_token)


class SummarizeBucketUseCase:
    """Computes total object count and size by iterating the entire bucket.

    Demonstrates the GoF Iterator directly: the use case never sees S3's
    pagination tokens, only `has_next`/`next`, regardless of how many
    pages the bucket actually spans.
    """

    def __init__(self, source: S3ObjectSource, page_size: int = 1000) -> None:
        self._source = source
        self._page_size = page_size

    def execute(self) -> BucketSummary:
        iterator = S3KeyIterator(self._source, self._page_size)
        count = 0
        total_size = 0
        while iterator.has_next():
            obj = iterator.next()
            count += 1
            total_size += obj.size
        return BucketSummary(object_count=count, total_size_bytes=total_size)
