"""Concrete Builder implementations for SQL queries."""
from __future__ import annotations

from typing import Self

from query_builder.domain.entities import (
    InsertQuery,
    JoinClause,
    JoinType,
    OrderClause,
    OrderDirection,
    SelectQuery,
    UpdateQuery,
)
from query_builder.domain.interfaces import (
    InsertQueryBuilder,
    SelectQueryBuilder,
    UpdateQueryBuilder,
)


class ConcreteSelectQueryBuilder(SelectQueryBuilder):
    """Builds SELECT queries step by step with a fluent interface.

    Each method returns `self` so calls can be chained:
        builder.select("id", "name").from_table("users").where("active = true").build()
    """

    def __init__(self) -> None:
        self._columns: list[str] = []
        self._table: str = ""
        self._joins: list[JoinClause] = []
        self._conditions: list[str] = []
        self._order_clauses: list[OrderClause] = []
        self._limit: int | None = None
        self._offset: int | None = None

    def select(self, *columns: str) -> Self:
        self._columns = list(columns)
        return self

    def from_table(self, table: str) -> Self:
        self._table = table
        return self

    def where(self, condition: str) -> Self:
        self._conditions.append(condition)
        return self

    def join(
        self,
        table: str,
        on_condition: str,
        join_type: JoinType = JoinType.INNER,
    ) -> Self:
        self._joins.append(JoinClause(table=table, on_condition=on_condition, join_type=join_type))
        return self

    def order_by(
        self,
        column: str,
        direction: OrderDirection = OrderDirection.ASC,
    ) -> Self:
        self._order_clauses.append(OrderClause(column=column, direction=direction))
        return self

    def limit(self, count: int) -> Self:
        self._limit = count
        return self

    def offset(self, skip: int) -> Self:
        self._offset = skip
        return self

    def build(self) -> SelectQuery:
        if not self._table:
            raise ValueError("A table name is required — call from_table() before build().")
        return SelectQuery(
            columns=self._columns,
            table=self._table,
            joins=self._joins,
            conditions=self._conditions,
            order_clauses=self._order_clauses,
            row_limit=self._limit,
            offset=self._offset,
        )


class ConcreteInsertQueryBuilder(InsertQueryBuilder):
    """Builds INSERT queries step by step."""

    def __init__(self) -> None:
        self._table: str = ""
        self._columns: list[str] = []
        self._rows: list[list[str]] = []

    def into(self, table: str) -> Self:
        self._table = table
        return self

    def columns(self, *cols: str) -> Self:
        self._columns = list(cols)
        return self

    def values(self, *row: str) -> Self:
        self._rows.append(list(row))
        return self

    def build(self) -> InsertQuery:
        if not self._table:
            raise ValueError("A table name is required — call into() before build().")
        if not self._columns:
            raise ValueError("At least one column is required — call columns() before build().")
        return InsertQuery(table=self._table, columns=self._columns, values=self._rows)


class ConcreteUpdateQueryBuilder(UpdateQueryBuilder):
    """Builds UPDATE queries step by step."""

    def __init__(self) -> None:
        self._table: str = ""
        self._assignments: dict[str, str] = {}
        self._conditions: list[str] = []

    def table(self, name: str) -> Self:
        self._table = name
        return self

    def set(self, column: str, value: str) -> Self:
        self._assignments[column] = value
        return self

    def where(self, condition: str) -> Self:
        self._conditions.append(condition)
        return self

    def build(self) -> UpdateQuery:
        if not self._table:
            raise ValueError("A table name is required — call table() before build().")
        if not self._assignments:
            raise ValueError("At least one assignment is required — call set() before build().")
        return UpdateQuery(
            table=self._table,
            assignments=self._assignments,
            conditions=self._conditions,
        )
