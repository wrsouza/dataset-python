"""Core entities for the S3 bucket iteration domain."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class S3Object:
    """A single S3 object — the element type this Iterator traverses."""

    key: str
    size: int
    last_modified: datetime


@dataclass(frozen=True)
class ObjectsPage:
    """One page of S3 objects plus the continuation token, if any."""

    items: list[S3Object]
    next_token: str | None


@dataclass(frozen=True)
class BucketSummary:
    """Aggregate statistics computed by iterating an entire bucket."""

    object_count: int
    total_size_bytes: int
