"""Shared pytest fixtures for the Data Source Bridge test suite."""

from __future__ import annotations

import pytest

from data_view.domain.entities import ConnectionConfig, QueryResult, Record


@pytest.fixture
def sample_config() -> ConnectionConfig:
    """A generic connection config usable by either implementor in tests."""
    return ConnectionConfig(
        host="localhost",
        port=1234,
        database="testdb",
        username="user",
        password="pass",
    )


@pytest.fixture
def sample_query_result() -> QueryResult:
    """A small two-record result used across unit tests."""
    records = [
        Record(fields={"name": "Alice", "age": 30}),
        Record(fields={"name": "Bob", "age": 25}),
    ]
    return QueryResult(source_name="Fake", records=records)
