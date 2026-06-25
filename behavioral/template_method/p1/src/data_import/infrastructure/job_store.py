"""In-memory job store for tracking import job status."""

from __future__ import annotations

from threading import Lock
from typing import ClassVar

from data_import.domain.entities import ImportResult


class JobStore:
    """Thread-safe in-memory store for import job results.

    In production, replace with Redis or a database-backed store.
    """

    _store: ClassVar[dict[str, ImportResult]] = {}
    _lock: ClassVar[Lock] = Lock()

    @classmethod
    def save(cls, result: ImportResult) -> None:
        with cls._lock:
            cls._store[result.job_id] = result

    @classmethod
    def get(cls, job_id: str) -> ImportResult | None:
        with cls._lock:
            return cls._store.get(job_id)
