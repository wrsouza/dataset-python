"""AbstractClass for the Template Method pattern — ETLPipeline.

Template Method defines the skeleton of the ETL algorithm in `run()`.
Subclasses override `extract()`, `transform()`, and `load()` — each
pipeline reads from and writes to its own staging/target tables —
without changing the overall flow or the Kafka completion event.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from etl_pipeline_template.domain.entities import ETLResult, RawRecord


class ETLPipeline(ABC):
    """AbstractClass: defines the `run()` template method.

    Fixed steps (always run in this order):
        1. extract    — abstract, subclass-specific staging source
        2. transform  — abstract, subclass-specific field mapping
        3. load       — abstract, subclass-specific target table
        4. emit_completion_event — concrete, shared Kafka notification (via Celery)

    Hook:
        should_emit_event() — returns True (default) to publish a
                               completion event; subclasses may override
                               to skip it (e.g. dry runs).
    """

    @abstractmethod
    def extract(self) -> list[RawRecord]:
        """Read raw records from this pipeline's staging source."""

    @abstractmethod
    def transform(self, records: list[RawRecord]) -> list[dict[str, Any]]:
        """Map raw records into the shape the target table expects."""

    @abstractmethod
    def load(self, records: list[dict[str, Any]]) -> int:
        """Persist transformed records; return the count actually loaded."""

    @abstractmethod
    def get_name(self) -> str:
        """Return the canonical name of this pipeline."""

    # ── Hook ────────────────────────────────────────────────────────────────────

    def should_emit_event(self) -> bool:
        """Whether to publish a completion event after a successful run."""
        return True

    # ── Concrete step ────────────────────────────────────────────────────────────

    def emit_completion_event(self, result: ETLResult) -> None:
        from etl_pipeline_template.infrastructure.celery_app import (
            publish_etl_completion_task,
        )

        publish_etl_completion_task.delay(result.pipeline_name, result.records_loaded)

    # ── Template Method ─────────────────────────────────────────────────────────

    def run(self) -> ETLResult:
        """Template method — defines the fixed extract/transform/load algorithm."""
        raw_records = self.extract()
        transformed = self.transform(raw_records)
        loaded_count = self.load(transformed)

        result = ETLResult(
            pipeline_name=self.get_name(),
            records_extracted=len(raw_records),
            records_loaded=loaded_count,
        )

        if self.should_emit_event():
            self.emit_completion_event(result)

        return result
