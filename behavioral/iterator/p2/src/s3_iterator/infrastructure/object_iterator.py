"""Concrete Iterator: lazily walks every S3 object, paging on demand."""

from __future__ import annotations

from collections import deque

from s3_iterator.domain.entities import S3Object
from s3_iterator.domain.interfaces import S3ObjectIterator, S3ObjectSource


class S3KeyIterator(S3ObjectIterator):
    """Traverses every object in a bucket one at a time.

    Internally fetches batches of `page_size` keys from the source as
    the buffer empties — the client only ever sees `has_next`/`next`,
    never the S3 `ContinuationToken` pagination underneath.
    """

    def __init__(self, source: S3ObjectSource, page_size: int = 1000) -> None:
        self._source = source
        self._page_size = page_size
        self._buffer: deque[S3Object] = deque()
        self._token: str | None = None
        self._exhausted = False

    def has_next(self) -> bool:
        if not self._buffer and not self._exhausted:
            self._load_next_page()
        return bool(self._buffer)

    def next(self) -> S3Object:
        if not self.has_next():
            raise StopIteration("No more objects to iterate")
        return self._buffer.popleft()

    def _load_next_page(self) -> None:
        items, next_token = self._source.fetch_page(self._token, self._page_size)
        self._buffer.extend(items)
        self._token = next_token
        if next_token is None:
            self._exhausted = True
