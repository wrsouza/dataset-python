"""Domain entities for the SQL Query Builder."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class JoinType(str, Enum):
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL OUTER JOIN"


class OrderDirection(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


@dataclass
class JoinClause:
    table: str
    on_condition: str
    join_type: JoinType = JoinType.INNER


@dataclass
class OrderClause:
    column: str
    direction: OrderDirection = OrderDirection.ASC


@dataclass
class SelectQuery:
    """Represents a fully built SELECT SQL query."""

    columns: list[str]
    table: str
    joins: list[JoinClause] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    order_clauses: list[OrderClause] = field(default_factory=list)
    row_limit: int | None = None
    offset: int | None = None

    def to_sql(self) -> str:
        """Render the query as a SQL string."""
        cols = ", ".join(self.columns) if self.columns else "*"
        parts = [f"SELECT {cols}", f"FROM {self.table}"]

        for join in self.joins:
            parts.append(f"{join.join_type.value} {join.table} ON {join.on_condition}")

        if self.conditions:
            where = " AND ".join(f"({c})" for c in self.conditions)
            parts.append(f"WHERE {where}")

        if self.order_clauses:
            order_items = [f"{o.column} {o.direction.value}" for o in self.order_clauses]
            parts.append(f"ORDER BY {', '.join(order_items)}")

        if self.row_limit is not None:
            parts.append(f"LIMIT {self.row_limit}")

        if self.offset is not None:
            parts.append(f"OFFSET {self.offset}")

        return "\n".join(parts)


@dataclass
class InsertQuery:
    """Represents a fully built INSERT SQL query."""

    table: str
    columns: list[str]
    values: list[list[str]]

    def to_sql(self) -> str:
        cols = ", ".join(self.columns)
        rows = [f"({', '.join(row)})" for row in self.values]
        return f"INSERT INTO {self.table} ({cols})\nVALUES {', '.join(rows)}"


@dataclass
class UpdateQuery:
    """Represents a fully built UPDATE SQL query."""

    table: str
    assignments: dict[str, str]
    conditions: list[str] = field(default_factory=list)

    def to_sql(self) -> str:
        set_clause = ", ".join(f"{k} = {v}" for k, v in self.assignments.items())
        parts = [f"UPDATE {self.table}", f"SET {set_clause}"]
        if self.conditions:
            where = " AND ".join(f"({c})" for c in self.conditions)
            parts.append(f"WHERE {where}")
        return "\n".join(parts)


@dataclass
class QueryResult:
    """Wraps the generated SQL and any execution metadata."""

    sql: str
    report_name: str | None = None
    row_count: int = 0
    rows: list[dict[str, object]] = field(default_factory=list)
