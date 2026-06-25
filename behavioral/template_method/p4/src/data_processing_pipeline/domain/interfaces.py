"""AbstractClass for the Template Method pattern — DataProcessingPipeline.

Template Method defines the skeleton of the fetch/parse/clean/persist
algorithm in `process()`. Subclasses override `fetch_input()`,
`parse()`, and `clean()` — each format reads its own S3 object shape —
without changing the overall flow or the shared MySQL persistence step.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol

from data_processing_pipeline.domain.entities import ProcessingResult
from data_processing_pipeline.domain.exceptions import EmptyInputAbortedError


class ProcessedRecordRepositoryLike(Protocol):
    """Minimal contract `persist()` relies on — lets tests inject an
    in-memory fake instead of a real MySQL/sqlite connection."""

    def bulk_insert(self, pipeline_name: str, records: list[dict[str, Any]]) -> int: ...


class DataProcessingPipeline(ABC):
    """AbstractClass: defines the `process()` template method.

    Fixed steps (always run in this order):
        1. fetch_input — abstract, subclass-specific (reads bytes from S3)
        2. parse       — abstract, subclass-specific (CSV/JSON/...)
        3. clean        — abstract, subclass-specific filtering/normalising
        4. persist      — concrete, shared MySQL logic

    Hook:
        on_empty_input() — returns True (default) to continue and persist
                            zero records; subclasses may override to abort.
    """

    def __init__(self, repository: ProcessedRecordRepositoryLike | None = None) -> None:
        self._repository = repository

    @abstractmethod
    def fetch_input(self) -> bytes:
        """Read the raw object bytes from S3."""

    @abstractmethod
    def parse(self, raw: bytes) -> list[dict[str, Any]]:
        """Parse raw bytes into a list of record dicts."""

    @abstractmethod
    def clean(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Drop/normalise records before persistence."""

    @abstractmethod
    def get_name(self) -> str:
        """Return the canonical name of this pipeline."""

    # ── Hook ────────────────────────────────────────────────────────────────────

    def on_empty_input(self) -> bool:
        """Whether to continue (persisting zero records) when `parse()`
        returns no records at all."""
        return True

    # ── Concrete step ────────────────────────────────────────────────────────────

    def persist(self, records: list[dict[str, Any]]) -> int:
        repository = self._repository or self._build_default_repository()
        return repository.bulk_insert(self.get_name(), records)

    @staticmethod
    def _build_default_repository() -> ProcessedRecordRepositoryLike:
        from data_processing_pipeline.infrastructure.repository import (
            ProcessedRecordRepository,
        )

        return ProcessedRecordRepository()

    # ── Template Method ─────────────────────────────────────────────────────────

    def process(self) -> ProcessingResult:
        raw = self.fetch_input()
        records = self.parse(raw)

        if not records and not self.on_empty_input():
            raise EmptyInputAbortedError(self.get_name())

        cleaned = self.clean(records)
        persisted = self.persist(cleaned)

        return ProcessingResult(
            pipeline_name=self.get_name(),
            records_processed=len(records),
            records_persisted=persisted,
        )
