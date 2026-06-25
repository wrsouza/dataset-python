"""Domain entities for the ETL Pipeline Template."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class RawRecord:
    """A single record as read from the staging source, before transformation."""

    source_id: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class ETLResult:
    """Immutable outcome of running an ETL pipeline once."""

    pipeline_name: str
    records_extracted: int
    records_loaded: int
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
