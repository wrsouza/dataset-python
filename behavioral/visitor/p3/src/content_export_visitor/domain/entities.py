"""Domain entities for the Content Export Visitor system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class ExportJob:
    """Immutable record of one content export run, uploaded to S3."""

    job_id: str
    format_name: str
    s3_key: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
