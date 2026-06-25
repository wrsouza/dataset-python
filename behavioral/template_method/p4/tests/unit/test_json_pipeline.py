"""Unit tests for JSONDataProcessingPipeline, against in-memory fakes."""

from __future__ import annotations

from typing import Any

from data_processing_pipeline.application.pipelines.json_pipeline import (
    JSONDataProcessingPipeline,
)


class FakeBody:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self) -> bytes:
        return self._data


class FakeS3Client:
    def __init__(self, content: bytes) -> None:
        self._content = content

    def get_object(self, Bucket: str, Key: str) -> dict[str, object]:
        return {"Body": FakeBody(self._content)}


class FakeRepository:
    def __init__(self) -> None:
        self.records: list[tuple[str, list[dict[str, Any]]]] = []

    def bulk_insert(self, pipeline_name: str, records: list[dict[str, Any]]) -> int:
        self.records.append((pipeline_name, records))
        return len(records)


def test_process_parses_json_lines_and_filters_missing_id() -> None:
    content = b'{"id": 1, "name": "Ana"}\n{"name": "no id"}\n{"id": 2, "name": "Bob"}\n'
    repository = FakeRepository()
    pipeline = JSONDataProcessingPipeline(
        FakeS3Client(content), "bucket", "key.jsonl", repository
    )

    result = pipeline.process()

    assert result.records_processed == 3
    assert result.records_persisted == 2
    assert repository.records[0][1] == [
        {"id": 1, "name": "Ana"},
        {"id": 2, "name": "Bob"},
    ]


def test_process_with_empty_input_persists_zero_records() -> None:
    pipeline = JSONDataProcessingPipeline(
        FakeS3Client(b""), "bucket", "key.jsonl", FakeRepository()
    )

    result = pipeline.process()

    assert result.records_processed == 0
    assert result.records_persisted == 0
