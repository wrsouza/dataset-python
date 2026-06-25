"""Composition helpers: build DataView instances wired to a concrete DataSource.

Centralizing construction here keeps `if isinstance` / `if type ==` checks
out of the application layer (Open/Closed) and out of the Streamlit UI.
"""

from __future__ import annotations

from data_view.application.use_cases import SummarizedDataView
from data_view.domain.entities import ConnectionConfig
from data_view.infrastructure.mongodb_source import MongoDataSource
from data_view.infrastructure.sqlserver_source import SqlServerDataSource


def build_sqlserver_view(config: ConnectionConfig) -> SummarizedDataView:
    """Build a SummarizedDataView backed by SQL Server."""
    return SummarizedDataView(SqlServerDataSource(config))


def build_mongodb_view(config: ConnectionConfig) -> SummarizedDataView:
    """Build a SummarizedDataView backed by MongoDB."""
    return SummarizedDataView(MongoDataSource(config))


def build_default_views(
    sqlserver_config: ConnectionConfig, mongodb_config: ConnectionConfig
) -> dict[str, SummarizedDataView]:
    """Build the registry of data views offered for selection in the UI."""
    return {
        "SQL Server": build_sqlserver_view(sqlserver_config),
        "MongoDB": build_mongodb_view(mongodb_config),
    }
