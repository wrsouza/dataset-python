"""Integration tests for the Data Source Bridge.

These tests exercise the full stack domain -> application -> infrastructure
through `infrastructure.factory`, for both concrete Implementors
(SqlServerDataSource and MongoDataSource). No real database is contacted:
SQL Server is mocked via `unittest.mock` (fake `pyodbc` module) and MongoDB
is exercised with `mongomock`, the same fake driver already used by the
unit tests in `tests/unit/test_mongodb_source.py`.
"""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest

from data_view.application.use_cases import (
    ListAvailableSourcesUseCase,
    LoadReportUseCase,
)
from data_view.domain.entities import ConnectionConfig
from data_view.infrastructure.factory import (
    build_default_views,
    build_mongodb_view,
    build_sqlserver_view,
)


@pytest.fixture
def fake_pyodbc(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Install a fake `pyodbc` module so SqlServerDataSource can connect."""
    module = ModuleType("pyodbc")
    mock_connect = MagicMock(name="pyodbc.connect")
    module.connect = mock_connect  # type: ignore[attr-defined]
    module.Error = Exception  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "pyodbc", module)
    return mock_connect


@pytest.fixture
def sqlserver_config() -> ConnectionConfig:
    """Connection config for the SQL Server implementor."""
    return ConnectionConfig(
        host="localhost",
        port=1433,
        database="reports",
        username="sa",
        password="pass",
    )


@pytest.fixture
def mongodb_config() -> ConnectionConfig:
    """Connection config for the MongoDB implementor."""
    return ConnectionConfig(
        host="localhost",
        port=27017,
        database="reports",
        extra={"uri": "mongodb://localhost:27017"},
    )


def test_load_report_use_case_through_sqlserver_view(
    fake_pyodbc: MagicMock, sqlserver_config: ConnectionConfig
) -> None:
    connection = MagicMock()
    cursor = MagicMock()
    cursor.description = [("name", None), ("age", None)]
    cursor.fetchall.return_value = [("Alice", 30), ("Bob", 25)]
    connection.cursor.return_value = cursor
    fake_pyodbc.return_value = connection

    view = build_sqlserver_view(sqlserver_config)
    use_case = LoadReportUseCase(view)

    result = use_case.execute("customers", {"active": True})

    assert result.source_name == "SQL Server"
    assert result.to_rows() == [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
    ]
    connection.close.assert_called_once()


def test_load_with_summary_through_sqlserver_view(
    fake_pyodbc: MagicMock, sqlserver_config: ConnectionConfig
) -> None:
    connection = MagicMock()
    cursor = MagicMock()
    cursor.description = [("name", None)]
    cursor.fetchall.return_value = [("Alice",)]
    connection.cursor.return_value = cursor
    fake_pyodbc.return_value = connection

    view = build_sqlserver_view(sqlserver_config)

    result, summary = view.load_with_summary("customers", {})

    assert len(result.records) == 1
    assert "1 registro(s) de 'customers' via SQL Server" == summary


def test_load_report_use_case_through_mongodb_view(
    monkeypatch: pytest.MonkeyPatch, mongodb_config: ConnectionConfig
) -> None:
    import mongomock

    monkeypatch.setattr("pymongo.MongoClient", mongomock.MongoClient, raising=False)

    view = build_mongodb_view(mongodb_config)
    use_case = LoadReportUseCase(view)

    # Seed data through the same client the implementor will use.
    seed_client = mongomock.MongoClient()
    monkeypatch.setattr("pymongo.MongoClient", lambda *_a, **_kw: seed_client)
    seed_client[mongodb_config.database]["customers"].insert_one(
        {"name": "Carol", "age": 40}
    )

    result = use_case.execute("customers", {})

    assert result.source_name == "MongoDB"
    rows = result.to_rows()
    assert len(rows) == 1
    assert rows[0]["name"] == "Carol"
    assert isinstance(rows[0]["_id"], str)


def test_load_with_summary_through_mongodb_view(
    monkeypatch: pytest.MonkeyPatch, mongodb_config: ConnectionConfig
) -> None:
    import mongomock

    shared_client = mongomock.MongoClient()
    monkeypatch.setattr("pymongo.MongoClient", lambda *_a, **_kw: shared_client)
    shared_client[mongodb_config.database]["orders"].insert_one({"total": 9.99})

    view = build_mongodb_view(mongodb_config)

    result, summary = view.load_with_summary("orders", {})

    assert len(result.records) == 1
    assert summary == "1 registro(s) de 'orders' via MongoDB"


def test_build_default_views_registers_both_sources(
    monkeypatch: pytest.MonkeyPatch,
    sqlserver_config: ConnectionConfig,
    mongodb_config: ConnectionConfig,
) -> None:
    import mongomock

    monkeypatch.setattr("pymongo.MongoClient", mongomock.MongoClient, raising=False)

    views = build_default_views(sqlserver_config, mongodb_config)
    list_use_case = ListAvailableSourcesUseCase(views)

    assert list_use_case.execute() == ["SQL Server", "MongoDB"]
    assert views["SQL Server"].source_name() == "SQL Server"
    assert views["MongoDB"].source_name() == "MongoDB"


def test_empty_collection_name_is_rejected_for_each_implementor(
    fake_pyodbc: MagicMock,
    sqlserver_config: ConnectionConfig,
    mongodb_config: ConnectionConfig,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import mongomock

    from data_view.application.use_cases import EmptyCollectionNameError

    monkeypatch.setattr("pymongo.MongoClient", mongomock.MongoClient, raising=False)

    sqlserver_view = build_sqlserver_view(sqlserver_config)
    mongodb_view = build_mongodb_view(mongodb_config)

    with pytest.raises(EmptyCollectionNameError):
        sqlserver_view.load("  ", {})

    with pytest.raises(EmptyCollectionNameError):
        mongodb_view.load("  ", {})
