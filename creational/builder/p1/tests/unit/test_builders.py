"""Unit tests for SQL Query Builder — no external services required."""
from __future__ import annotations

import pytest

from query_builder.application.use_cases import BuildQueryUseCase, ReportQueryDirector
from query_builder.domain.entities import JoinType, OrderDirection
from query_builder.infrastructure.builders import (
    ConcreteInsertQueryBuilder,
    ConcreteSelectQueryBuilder,
    ConcreteUpdateQueryBuilder,
)


class TestConcreteSelectQueryBuilder:
    def test_simple_select_all(self) -> None:
        query = ConcreteSelectQueryBuilder().from_table("users").build()
        sql = query.to_sql()
        assert "SELECT *" in sql
        assert "FROM users" in sql

    def test_select_with_columns(self) -> None:
        query = (
            ConcreteSelectQueryBuilder()
            .select("id", "name", "email")
            .from_table("users")
            .build()
        )
        assert "SELECT id, name, email" in query.to_sql()

    def test_where_clause(self) -> None:
        query = (
            ConcreteSelectQueryBuilder()
            .from_table("orders")
            .where("status = 'active'")
            .build()
        )
        assert "WHERE" in query.to_sql()
        assert "status = 'active'" in query.to_sql()

    def test_multiple_where_conditions_joined_with_and(self) -> None:
        query = (
            ConcreteSelectQueryBuilder()
            .from_table("orders")
            .where("status = 'active'")
            .where("total > 100")
            .build()
        )
        sql = query.to_sql()
        assert "AND" in sql

    def test_inner_join(self) -> None:
        query = (
            ConcreteSelectQueryBuilder()
            .from_table("orders o")
            .join("customers c", "c.id = o.customer_id")
            .build()
        )
        sql = query.to_sql()
        assert "INNER JOIN customers c ON c.id = o.customer_id" in sql

    def test_left_join(self) -> None:
        query = (
            ConcreteSelectQueryBuilder()
            .from_table("orders o")
            .join("customers c", "c.id = o.customer_id", JoinType.LEFT)
            .build()
        )
        assert "LEFT JOIN" in query.to_sql()

    def test_order_by_desc(self) -> None:
        query = (
            ConcreteSelectQueryBuilder()
            .from_table("products")
            .order_by("price", OrderDirection.DESC)
            .build()
        )
        assert "ORDER BY price DESC" in query.to_sql()

    def test_limit_and_offset(self) -> None:
        query = (
            ConcreteSelectQueryBuilder()
            .from_table("products")
            .limit(10)
            .offset(20)
            .build()
        )
        sql = query.to_sql()
        assert "LIMIT 10" in sql
        assert "OFFSET 20" in sql

    def test_build_raises_when_no_table(self) -> None:
        with pytest.raises(ValueError, match="table name is required"):
            ConcreteSelectQueryBuilder().build()

    def test_method_chaining_returns_self(self) -> None:
        builder = ConcreteSelectQueryBuilder()
        result = builder.select("id").from_table("t").where("x=1").limit(5)
        assert result is builder


class TestConcreteInsertQueryBuilder:
    def test_basic_insert(self) -> None:
        query = (
            ConcreteInsertQueryBuilder()
            .into("users")
            .columns("name", "email")
            .values("'Alice'", "'alice@example.com'")
            .build()
        )
        sql = query.to_sql()
        assert "INSERT INTO users" in sql
        assert "name, email" in sql
        assert "'Alice'" in sql

    def test_multiple_rows(self) -> None:
        query = (
            ConcreteInsertQueryBuilder()
            .into("tags")
            .columns("name")
            .values("'python'")
            .values("'design-patterns'")
            .build()
        )
        assert "VALUES" in query.to_sql()

    def test_build_raises_when_no_table(self) -> None:
        with pytest.raises(ValueError, match="table name is required"):
            ConcreteInsertQueryBuilder().columns("x").values("1").build()

    def test_build_raises_when_no_columns(self) -> None:
        with pytest.raises(ValueError, match="At least one column"):
            ConcreteInsertQueryBuilder().into("t").build()


class TestConcreteUpdateQueryBuilder:
    def test_basic_update(self) -> None:
        query = (
            ConcreteUpdateQueryBuilder()
            .table("users")
            .set("name", "'Bob'")
            .where("id = 1")
            .build()
        )
        sql = query.to_sql()
        assert "UPDATE users" in sql
        assert "SET name = 'Bob'" in sql
        assert "WHERE" in sql

    def test_build_raises_when_no_table(self) -> None:
        with pytest.raises(ValueError, match="table name is required"):
            ConcreteUpdateQueryBuilder().set("x", "1").build()

    def test_build_raises_when_no_assignments(self) -> None:
        with pytest.raises(ValueError, match="At least one assignment"):
            ConcreteUpdateQueryBuilder().table("t").build()


class TestReportQueryDirector:
    def test_sales_by_period_contains_date_filters(self) -> None:
        director = ReportQueryDirector(ConcreteSelectQueryBuilder())
        query = director.build_sales_by_period("2024-01-01", "2024-12-31")
        sql = query.to_sql()
        assert "2024-01-01" in sql
        assert "2024-12-31" in sql
        assert "orders" in sql

    def test_top_customers_has_limit(self) -> None:
        director = ReportQueryDirector(ConcreteSelectQueryBuilder())
        query = director.build_top_customers(top_n=5)
        assert "LIMIT 5" in query.to_sql()

    def test_low_stock_products_has_threshold(self) -> None:
        director = ReportQueryDirector(ConcreteSelectQueryBuilder())
        query = director.build_low_stock_products(threshold=20)
        assert "20" in query.to_sql()


class TestBuildQueryUseCase:
    def test_execute_from_spec(self) -> None:
        spec = {"table": "orders", "columns": ["id", "status"], "conditions": [], "limit": 10}
        result = BuildQueryUseCase(ConcreteSelectQueryBuilder()).execute(spec)
        assert "SELECT id, status" in result.sql
        assert "FROM orders" in result.sql
        assert "LIMIT 10" in result.sql
