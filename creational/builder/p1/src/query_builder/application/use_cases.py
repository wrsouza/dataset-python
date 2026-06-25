"""Application layer — Director and use cases for query building."""
from __future__ import annotations

from query_builder.domain.entities import OrderDirection, QueryResult, SelectQuery
from query_builder.domain.interfaces import SelectQueryBuilder


class ReportQueryDirector:
    """Director that orchestrates common report queries using any SelectQueryBuilder.

    The Director knows the construction steps; it does NOT know
    which concrete builder is used (Dependency Inversion Principle).
    """

    def __init__(self, builder: SelectQueryBuilder) -> None:
        self._builder = builder

    def build_sales_by_period(self, start_date: str, end_date: str) -> SelectQuery:
        """Assembles a standard sales-by-period report query."""
        return (
            self._builder
            .select(
                "o.id",
                "o.created_at",
                "o.total_amount",
                "c.name AS customer_name",
            )
            .from_table("orders o")
            .join("customers c", "c.id = o.customer_id")
            .where(f"o.created_at >= '{start_date}'")
            .where(f"o.created_at <= '{end_date}'")
            .order_by("o.created_at", OrderDirection.DESC)
            .build()
        )

    def build_top_customers(self, top_n: int = 10) -> SelectQuery:
        """Assembles a query that ranks customers by total spend."""
        return (
            self._builder
            .select(
                "c.id",
                "c.name",
                "SUM(o.total_amount) AS total_spent",
                "COUNT(o.id) AS order_count",
            )
            .from_table("customers c")
            .join("orders o", "o.customer_id = c.id")
            .order_by("total_spent", OrderDirection.DESC)
            .limit(top_n)
            .build()
        )

    def build_low_stock_products(self, threshold: int = 10) -> SelectQuery:
        """Assembles a query for products with stock below a given threshold."""
        return (
            self._builder
            .select("id", "name", "sku", "stock_quantity")
            .from_table("products")
            .where(f"stock_quantity < {threshold}")
            .order_by("stock_quantity", OrderDirection.ASC)
            .build()
        )


class BuildQueryUseCase:
    """Builds a query from a JSON specification and returns SQL."""

    def __init__(self, builder: SelectQueryBuilder) -> None:
        self._builder = builder

    def execute(self, spec: dict[str, object]) -> QueryResult:
        """Parse a JSON spec and produce the SQL string."""
        columns: list[str] = spec.get("columns", [])  # type: ignore[assignment]
        table: str = spec.get("table", "")  # type: ignore[assignment]
        conditions: list[str] = spec.get("conditions", [])  # type: ignore[assignment]
        order_by: str | None = spec.get("order_by")  # type: ignore[assignment]
        limit: int | None = spec.get("limit")  # type: ignore[assignment]

        self._builder.select(*columns).from_table(table)

        for condition in conditions:
            self._builder.where(condition)

        if order_by:
            self._builder.order_by(order_by)

        if limit is not None:
            self._builder.limit(limit)

        query = self._builder.build()
        return QueryResult(sql=query.to_sql())
