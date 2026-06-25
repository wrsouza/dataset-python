"""Unit tests for S3KeyIterator, the concrete GoF Iterator."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from s3_iterator.domain.entities import S3Object
from s3_iterator.domain.interfaces import S3ObjectSource
from s3_iterator.infrastructure.object_iterator import S3KeyIterator


class FakeS3ObjectSource(S3ObjectSource):
    """An in-memory S3ObjectSource that paginates a fixed list of keys."""

    def __init__(self, total: int) -> None:
        now = datetime(2026, 1, 1, tzinfo=UTC)
        self._objects = [
            S3Object(key=f"file-{i:03d}.txt", size=i, last_modified=now)
            for i in range(total)
        ]
        self.fetch_calls = 0

    def fetch_page(
        self, continuation_token: str | None, limit: int
    ) -> tuple[list[S3Object], str | None]:
        self.fetch_calls += 1
        start = int(continuation_token) if continuation_token is not None else 0
        page = self._objects[start : start + limit]
        end = start + len(page)
        next_token = str(end) if end < len(self._objects) else None
        return page, next_token


def test_iterates_every_object_exactly_once() -> None:
    source = FakeS3ObjectSource(total=7)
    iterator = S3KeyIterator(source, page_size=3)

    seen = []
    while iterator.has_next():
        seen.append(iterator.next().key)

    assert seen == [f"file-{i:03d}.txt" for i in range(7)]


def test_fetches_pages_lazily_not_all_at_once() -> None:
    source = FakeS3ObjectSource(total=10)
    iterator = S3KeyIterator(source, page_size=4)

    iterator.next()

    assert source.fetch_calls == 1


def test_has_next_is_false_for_empty_bucket() -> None:
    source = FakeS3ObjectSource(total=0)
    iterator = S3KeyIterator(source, page_size=10)

    assert iterator.has_next() is False


def test_next_raises_stop_iteration_when_exhausted() -> None:
    source = FakeS3ObjectSource(total=1)
    iterator = S3KeyIterator(source, page_size=10)
    iterator.next()

    with pytest.raises(StopIteration):
        iterator.next()
