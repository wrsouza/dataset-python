"""Shared fixtures for Data Migration Facade tests — uses sqlite stand-ins."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from migration.application.facade import MigrationFacade
from migration.domain.entities import ConnectionConfig
from migration.infrastructure.connection_factory import DriverConnectionFactory
from migration.infrastructure.extractor import BatchDataExtractor
from migration.infrastructure.loader import GenericDataLoader
from migration.infrastructure.schema_analyzer import GenericSchemaAnalyzer
from migration.infrastructure.transformer import TrimmingTypeTransformer


@pytest.fixture
def source_db_path(tmp_path: object) -> str:
    path = str(tmp_path) + "/source.db"  # type: ignore[operator]
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE orders (id INTEGER PRIMARY KEY, customer TEXT, total REAL)"
    )
    conn.executemany(
        "INSERT INTO orders (id, customer, total) VALUES (?, ?, ?)",
        [(1, "  Alice  ", 10.5), (2, "Bob", 20.0), (3, "Carol", 30.0)],
    )
    conn.execute("CREATE TABLE empty_table (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def dest_db_path(tmp_path: object) -> str:
    path = str(tmp_path) + "/dest.db"  # type: ignore[operator]
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE orders (id INTEGER PRIMARY KEY, customer TEXT, total REAL)"
    )
    conn.execute("CREATE TABLE empty_table (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def source_config(source_db_path: str) -> ConnectionConfig:
    return ConnectionConfig(dialect="sqlite", dsn=source_db_path)


@pytest.fixture
def dest_config(dest_db_path: str) -> ConnectionConfig:
    return ConnectionConfig(dialect="sqlite", dsn=dest_db_path)


@pytest.fixture
def facade() -> MigrationFacade:
    return MigrationFacade(
        connection_factory=DriverConnectionFactory(),
        schema_analyzer=GenericSchemaAnalyzer(),
        extractor=BatchDataExtractor(),
        transformer=TrimmingTypeTransformer(),
        loader=GenericDataLoader(dialect="sqlite"),
    )


@pytest.fixture
def dest_connection(dest_db_path: str) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(dest_db_path)
    yield conn
    conn.close()
