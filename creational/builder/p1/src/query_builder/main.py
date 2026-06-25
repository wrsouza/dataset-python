"""FastAPI application entry point for the SQL Query Builder."""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from query_builder.application.use_cases import BuildQueryUseCase, ReportQueryDirector
from query_builder.domain.entities import QueryResult
from query_builder.infrastructure.builders import ConcreteSelectQueryBuilder

app = FastAPI(
    title="SQL Query Builder API",
    description="Demonstrates the Builder pattern with a fluent SQL query builder.",
    version="1.0.0",
)

AVAILABLE_REPORTS = ["sales_by_period", "top_customers", "low_stock_products"]


class QuerySpec(BaseModel):
    columns: list[str] = []
    table: str
    conditions: list[str] = []
    order_by: str | None = None
    limit: int | None = None


class SalesByPeriodParams(BaseModel):
    start_date: str
    end_date: str


@app.post("/queries/build", response_model=dict[str, Any])
def build_query(spec: QuerySpec) -> dict[str, Any]:
    """Build a SELECT query from a JSON specification."""
    builder = ConcreteSelectQueryBuilder()
    use_case = BuildQueryUseCase(builder)
    try:
        result: QueryResult = use_case.execute(spec.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"sql": result.sql}


@app.get("/queries/reports/{report_name}", response_model=dict[str, Any])
def get_report_query(
    report_name: str,
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31",
    top_n: int = 10,
    threshold: int = 10,
) -> dict[str, Any]:
    """Return a pre-built report SQL via the Director."""
    director = ReportQueryDirector(ConcreteSelectQueryBuilder())

    if report_name == "sales_by_period":
        query = director.build_sales_by_period(start_date, end_date)
    elif report_name == "top_customers":
        query = director.build_top_customers(top_n)
    elif report_name == "low_stock_products":
        query = director.build_low_stock_products(threshold)
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Report '{report_name}' not found. Available: {AVAILABLE_REPORTS}",
        )

    return {"report": report_name, "sql": query.to_sql()}


@app.get("/queries/reports", response_model=dict[str, Any])
def list_reports() -> dict[str, Any]:
    """List all available pre-built reports."""
    return {"reports": AVAILABLE_REPORTS}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
