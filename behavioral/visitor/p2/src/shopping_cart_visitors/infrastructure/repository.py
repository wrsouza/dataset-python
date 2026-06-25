"""Repository for cart operation reports — works against any DB-API 2.0
connection (sqlite3 or pymysql), same dialect-aware trick used in
`strategy/p2`."""

from __future__ import annotations

import json
from typing import Any

from shopping_cart_visitors.domain.entities import CartReport, OperationType

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS cart_report (
    id INTEGER PRIMARY KEY {auto_increment},
    operation VARCHAR(20) NOT NULL,
    data TEXT NOT NULL
)
"""


class CartReportRepository:
    def __init__(self, connection: Any, dialect: str = "sqlite") -> None:
        self._connection = connection
        self._placeholder = "%s" if dialect == "mysql" else "?"
        auto_increment = "AUTOINCREMENT" if dialect == "sqlite" else "AUTO_INCREMENT"
        cursor = self._connection.cursor()
        cursor.execute(_CREATE_TABLE_SQL.format(auto_increment=auto_increment))
        self._connection.commit()

    def save(self, report: CartReport) -> None:
        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT INTO cart_report (operation, data) "
            f"VALUES ({self._placeholder}, {self._placeholder})",
            (report.operation.value, json.dumps(report.data)),
        )
        self._connection.commit()

    def list_for_operation(self, operation: OperationType) -> list[CartReport]:
        cursor = self._connection.cursor()
        cursor.execute(
            f"SELECT data FROM cart_report WHERE operation = {self._placeholder}",
            (operation.value,),
        )
        return [
            CartReport(operation=operation, data=json.loads(row[0]))
            for row in cursor.fetchall()
        ]
