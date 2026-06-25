"""Abstractions for the Iterator pattern and the underlying S3 access."""

from __future__ import annotations

from abc import ABC, abstractmethod

from s3_iterator.domain.entities import S3Object


class S3ObjectIterator(ABC):
    """The Iterator: traverses every object in a bucket one at a time,

    without exposing how (or in what batches) S3 was actually paginated.
    """

    @abstractmethod
    def has_next(self) -> bool:
        """Return True if there is at least one more object to traverse."""

    @abstractmethod
    def next(self) -> S3Object:
        """Return the next object and advance the iterator's position."""


class S3ObjectSource(ABC):
    """The Aggregate's data-access boundary: lists bucket objects page by page."""

    @abstractmethod
    def fetch_page(
        self, continuation_token: str | None, limit: int
    ) -> tuple[list[S3Object], str | None]:
        """Return up to `limit` objects after the token, and the next token."""
