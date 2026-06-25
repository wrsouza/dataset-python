"""Unit tests for the on_empty_input hook and EmptyInputAbortedError."""

from __future__ import annotations

from typing import Any

import pytest

from data_processing_pipeline.domain.exceptions import EmptyInputAbortedError
from data_processing_pipeline.domain.interfaces import DataProcessingPipeline


class FakeRepository:
    def bulk_insert(self, pipeline_name: str, records: list[dict[str, Any]]) -> int:
        return len(records)


class AbortOnEmptyPipeline(DataProcessingPipeline):
    """A pipeline that always sees empty input and refuses to continue."""

    def fetch_input(self) -> bytes:
        return b""

    def parse(self, raw: bytes) -> list[dict[str, Any]]:
        return []

    def clean(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return records

    def get_name(self) -> str:
        return "abort_on_empty"

    def on_empty_input(self) -> bool:
        return False


def test_pipeline_aborts_when_hook_returns_false() -> None:
    pipeline = AbortOnEmptyPipeline(FakeRepository())

    with pytest.raises(EmptyInputAbortedError):
        pipeline.process()
