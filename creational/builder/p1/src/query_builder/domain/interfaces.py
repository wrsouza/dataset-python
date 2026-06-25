"""Abstract interfaces for the Builder pattern — SQL Query Builder."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self

from query_builder.domain.entities import (
    InsertQuery,
    JoinType,
    OrderDirection,
    SelectQuery,
    UpdateQuery,
)


class SelectQueryBuilder(ABC):
    """Builder interface for SELECT queries (SRP: only SELECT construction)."""

    @abstractmethod
    def select(self, *columns: str) -> Self: ...

    @abstractmethod
    def from_table(self, table: str) -> Self: ...

    @abstractmethod
    def where(self, condition: str) -> Self: ...

    @abstractmethod
    def join(
        self,
        table: str,
        on_condition: str,
        join_type: JoinType = JoinType.INNER,
    ) -> Self: ...

    @abstractmethod
    def order_by(
        self,
        column: str,
        direction: OrderDirection = OrderDirection.ASC,
    ) -> Self: ...

    @abstractmethod
    def limit(self, count: int) -> Self: ...

    @abstractmethod
    def offset(self, skip: int) -> Self: ...

    @abstractmethod
    def build(self) -> SelectQuery: ...


class InsertQueryBuilder(ABC):
    """Builder interface for INSERT queries (SRP: only INSERT construction)."""

    @abstractmethod
    def into(self, table: str) -> Self: ...

    @abstractmethod
    def columns(self, *cols: str) -> Self: ...

    @abstractmethod
    def values(self, *row: str) -> Self: ...

    @abstractmethod
    def build(self) -> InsertQuery: ...


class UpdateQueryBuilder(ABC):
    """Builder interface for UPDATE queries (SRP: only UPDATE construction)."""

    @abstractmethod
    def table(self, name: str) -> Self: ...

    @abstractmethod
    def set(self, column: str, value: str) -> Self: ...

    @abstractmethod
    def where(self, condition: str) -> Self: ...

    @abstractmethod
    def build(self) -> UpdateQuery: ...
