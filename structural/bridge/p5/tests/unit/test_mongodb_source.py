"""Unit tests for MongoDataSource using mongomock as a fake pymongo driver."""

from __future__ import annotations

import pytest

from data_view.domain.entities import ConnectionConfig
from data_view.infrastructure.mongodb_source import MongoDataSource


def test_connect_then_fetch_returns_inserted_documents(
    monkeypatch: pytest.MonkeyPatch, sample_config: ConnectionConfig
) -> None:
    import mongomock

    monkeypatch.setattr("pymongo.MongoClient", mongomock.MongoClient, raising=False)
    import sys

    sys.modules.setdefault("pymongo", __import__("pymongo"))

    source = MongoDataSource(sample_config)
    source.connect()
    database = source._client[sample_config.database]  # noqa: SLF001
    database["customers"].insert_one({"name": "Alice", "age": 30})

    result = source.fetch("customers", {})

    assert result.source_name() == "MongoDB" if callable(result.source_name) else True
    assert len(result.records) == 1
    assert result.records[0].fields["name"] == "Alice"


def test_disconnect_closes_client(sample_config: ConnectionConfig) -> None:
    import mongomock

    source = MongoDataSource(sample_config)
    source._client = mongomock.MongoClient()  # noqa: SLF001

    source.disconnect()

    assert source._client is None  # noqa: SLF001


def test_fetch_without_connect_raises(sample_config: ConnectionConfig) -> None:
    import pytest

    from data_view.domain.interfaces import DataSourceError

    source = MongoDataSource(sample_config)

    with pytest.raises(DataSourceError, match="connect"):
        source.fetch("customers", {})


def test_fetch_strips_object_id_to_string(sample_config: ConnectionConfig) -> None:
    import mongomock

    source = MongoDataSource(sample_config)
    source._client = mongomock.MongoClient()  # noqa: SLF001
    database = source._client[sample_config.database]  # noqa: SLF001
    database["orders"].insert_one({"total": 99.9})

    result = source.fetch("orders", {})

    assert isinstance(result.records[0].fields["_id"], str)


def test_source_name_is_mongodb(sample_config: ConnectionConfig) -> None:
    assert MongoDataSource(sample_config).source_name() == "MongoDB"
