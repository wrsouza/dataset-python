"""Repository for the discount application history.

Works against any DB-API 2.0 connection (sqlite3 or pymysql) — only
the placeholder style differs between dialects, so it's selected once
at construction time.
"""

from __future__ import annotations

from typing import Any

from discount_strategy_api.domain.entities import DiscountResult

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS discount_application (
    id INTEGER PRIMARY KEY {auto_increment},
    strategy_name VARCHAR(50) NOT NULL,
    original_total DOUBLE NOT NULL,
    discount_amount DOUBLE NOT NULL,
    final_total DOUBLE NOT NULL
)
"""


class DiscountHistoryRepository:
    def __init__(self, connection: Any, dialect: str = "sqlite") -> None:
        self._connection = connection
        self._placeholder = "%s" if dialect == "mysql" else "?"
        auto_increment = "AUTOINCREMENT" if dialect == "sqlite" else "AUTO_INCREMENT"
        cursor = self._connection.cursor()
        cursor.execute(_CREATE_TABLE_SQL.format(auto_increment=auto_increment))
        self._connection.commit()

    def append(self, result: DiscountResult) -> None:
        sql = (
            "INSERT INTO discount_application "
            "(strategy_name, original_total, discount_amount, final_total) "
            f"VALUES ({self._placeholder}, {self._placeholder}, "
            f"{self._placeholder}, {self._placeholder})"
        )
        cursor = self._connection.cursor()
        cursor.execute(
            sql,
            (
                result.strategy_name,
                result.original_total,
                result.discount_amount,
                result.final_total,
            ),
        )
        self._connection.commit()

    def list_all(self) -> list[DiscountResult]:
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT strategy_name, original_total, discount_amount, final_total "
            "FROM discount_application ORDER BY id ASC"
        )
        rows = cursor.fetchall()
        return [
            DiscountResult(
                strategy_name=row[0],
                original_total=row[1],
                discount_amount=row[2],
                final_total=row[3],
            )
            for row in rows
        ]
