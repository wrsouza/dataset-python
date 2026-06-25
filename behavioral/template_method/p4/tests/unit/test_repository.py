"""Unit tests for ProcessedRecordRepository against a real (in-memory
SQLite) DB-API connection."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from data_processing_pipeline.infrastructure.repository import (
    ProcessedRecordRepository,
)


@pytest.fixture
def connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def repository(connection: sqlite3.Connection) -> ProcessedRecordRepository:
    return ProcessedRecordRepository(connection, dialect="sqlite")


def test_bulk_insert_and_list_for_pipeline_round_trips(
    repository: ProcessedRecordRepository,
) -> None:
    count = repository.bulk_insert("csv_data_processing", [{"id": 1}, {"id": 2}])

    assert count == 2
    assert repository.list_for_pipeline("csv_data_processing") == [
        {"id": 1},
        {"id": 2},
    ]


def test_list_for_pipeline_only_returns_matching_pipeline(
    repository: ProcessedRecordRepository,
) -> None:
    repository.bulk_insert("csv_data_processing", [{"id": 1}])
    repository.bulk_insert("json_data_processing", [{"id": 2}])

    assert repository.list_for_pipeline("csv_data_processing") == [{"id": 1}]


def test_list_for_pipeline_empty_when_no_records(
    repository: ProcessedRecordRepository,
) -> None:
    assert repository.list_for_pipeline("unknown") == []
