"""Domain entities for the Data Processing Pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class ProcessingResult:
    """Immutable outcome of running a data processing pipeline once."""

    pipeline_name: str
    records_processed: int
    records_persisted: int
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
