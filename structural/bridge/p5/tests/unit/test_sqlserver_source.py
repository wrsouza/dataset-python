"""Unit tests for SqlServerDataSource using unittest.mock for pyodbc."""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest

from data_view.domain.entities import ConnectionConfig
from data_view.domain.interfaces import DataSourceError
from data_view.infrastructure.sqlserver_source import SqlServerDataSource


@pytest.fixture
def fake_pyodbc(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Install a fake `pyodbc` module so the source can be imported/tested."""
    module = ModuleType("pyodbc")
    mock_connect = MagicMock(name="pyodbc.connect")
    module.connect = mock_connect  # type: ignore[attr-defined]
    module.Error = Exception  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "pyodbc", module)
    return mock_connect


def test_connect_opens_pyodbc_connection(
    fake_pyodbc: MagicMock, sample_config: ConnectionConfig
) -> None:
    source = SqlServerDataSource(sample_config)
    source.connect()

    fake_pyodbc.assert_called_once()
    assert "testdb" in fake_pyodbc.call_args.args[0]


def test_connect_is_idempotent(
    fake_pyodbc: MagicMock, sample_config: ConnectionConfig
) -> None:
    source = SqlServerDataSource(sample_config)
    source.connect()
    source.connect()

    fake_pyodbc.assert_called_once()


def test_disconnect_closes_connection(
    fake_pyodbc: MagicMock, sample_config: ConnectionConfig
) -> None:
    connection = MagicMock()
    fake_pyodbc.return_value = connection
    source = SqlServerDataSource(sample_config)
    source.connect()

    source.disconnect()

    connection.close.assert_called_once()


def test_fetch_without_connect_raises(sample_config: ConnectionConfig) -> None:
    source = SqlServerDataSource(sample_config)

    with pytest.raises(DataSourceError, match="connect"):
        source.fetch("customers", {})


def test_fetch_maps_rows_to_records(
    fake_pyodbc: MagicMock, sample_config: ConnectionConfig
) -> None:
    connection = MagicMock()
    cursor = MagicMock()
    cursor.description = [("name", None), ("age", None)]
    cursor.fetchall.return_value = [("Alice", 30), ("Bob", 25)]
    connection.cursor.return_value = cursor
    fake_pyodbc.return_value = connection

    source = SqlServerDataSource(sample_config)
    source.connect()
    result = source.fetch("customers", {"active": True})

    assert result.source_name == "SQL Server"
    assert result.to_rows() == [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
    ]
    cursor.execute.assert_called_once()


def test_fetch_wraps_cursor_errors(
    fake_pyodbc: MagicMock, sample_config: ConnectionConfig
) -> None:
    connection = MagicMock()
    cursor = MagicMock()
    cursor.execute.side_effect = RuntimeError("syntax error")
    connection.cursor.return_value = cursor
    fake_pyodbc.return_value = connection

    source = SqlServerDataSource(sample_config)
    source.connect()

    with pytest.raises(DataSourceError, match="query failed"):
        source.fetch("customers", {})


def test_source_name_is_sql_server(sample_config: ConnectionConfig) -> None:
    assert SqlServerDataSource(sample_config).source_name() == "SQL Server"
