"""Repository for processed records — works against any DB-API 2.0
connection (sqlite3 or pymysql), same dialect-aware trick used in
`strategy/p2`."""

from __future__ import annotations

import json
import os
from typing import Any

from data_processing_pipeline.infrastructure.connection_factory import (
    build_connection,
)

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS processed_record (
    id INTEGER PRIMARY KEY {auto_increment},
    pipeline_name VARCHAR(100) NOT NULL,
    data TEXT NOT NULL
)
"""


class ProcessedRecordRepository:
    def __init__(
        self, connection: Any | None = None, dialect: str | None = None
    ) -> None:
        self._connection = connection or build_connection()
        self._dialect = dialect or os.environ.get("DB_DIALECT", "sqlite")
        self._placeholder = "%s" if self._dialect == "mysql" else "?"
        auto_increment = (
            "AUTOINCREMENT" if self._dialect == "sqlite" else "AUTO_INCREMENT"
        )
        cursor = self._connection.cursor()
        cursor.execute(_CREATE_TABLE_SQL.format(auto_increment=auto_increment))
        self._connection.commit()

    def bulk_insert(self, pipeline_name: str, records: list[dict[str, Any]]) -> int:
        cursor = self._connection.cursor()
        sql = (
            "INSERT INTO processed_record (pipeline_name, data) "
            f"VALUES ({self._placeholder}, {self._placeholder})"
        )
        for record in records:
            cursor.execute(sql, (pipeline_name, json.dumps(record)))
        self._connection.commit()
        return len(records)

    def list_for_pipeline(self, pipeline_name: str) -> list[dict[str, Any]]:
        cursor = self._connection.cursor()
        cursor.execute(
            f"SELECT data FROM processed_record WHERE pipeline_name = "
            f"{self._placeholder}",
            (pipeline_name,),
        )
        return [json.loads(row[0]) for row in cursor.fetchall()]
