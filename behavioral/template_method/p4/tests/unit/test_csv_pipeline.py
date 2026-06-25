"""Unit tests for CSVDataProcessingPipeline, against in-memory fakes."""

from __future__ import annotations

from typing import Any

from data_processing_pipeline.application.pipelines.csv_pipeline import (
    CSVDataProcessingPipeline,
)


class FakeBody:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self) -> bytes:
        return self._data


class FakeS3Client:
    def __init__(self, content: bytes) -> None:
        self._content = content
        self.calls: list[tuple[str, str]] = []

    def get_object(self, Bucket: str, Key: str) -> dict[str, object]:
        self.calls.append((Bucket, Key))
        return {"Body": FakeBody(self._content)}


class FakeRepository:
    def __init__(self) -> None:
        self.records: list[tuple[str, list[dict[str, Any]]]] = []

    def bulk_insert(self, pipeline_name: str, records: list[dict[str, Any]]) -> int:
        self.records.append((pipeline_name, records))
        return len(records)


def test_process_reads_parses_cleans_and_persists() -> None:
    csv_content = b"id,name\n1, Ana \n2,Bob\n"
    s3_client = FakeS3Client(csv_content)
    repository = FakeRepository()
    pipeline = CSVDataProcessingPipeline(s3_client, "bucket", "key.csv", repository)

    result = pipeline.process()

    assert result.records_processed == 2
    assert result.records_persisted == 2
    assert s3_client.calls == [("bucket", "key.csv")]
    assert repository.records[0][1][0]["name"] == "Ana"


def test_clean_drops_blank_rows() -> None:
    csv_content = b"id,name\n,\n2,Bob\n"
    pipeline = CSVDataProcessingPipeline(
        FakeS3Client(csv_content), "bucket", "key.csv", FakeRepository()
    )

    result = pipeline.process()

    assert result.records_processed == 2
    assert result.records_persisted == 1


def test_process_with_empty_csv_persists_zero_records() -> None:
    pipeline = CSVDataProcessingPipeline(
        FakeS3Client(b"id,name\n"), "bucket", "key.csv", FakeRepository()
    )

    result = pipeline.process()

    assert result.records_processed == 0
    assert result.records_persisted == 0
