"""FastAPI application entry-point for the Query AST Visitor service."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from query_ast.application.use_cases import AnalyzeQueryUseCase, UnknownOperationError
from query_ast.domain.entities import OperationType
from query_ast.infrastructure.visitors import (
    QueryExplainerVisitor,
    QueryOptimizerVisitor,
    QueryValidatorVisitor,
    SQLGeneratorVisitor,
)

# Composition root: maps each operation to its ConcreteVisitor class (DIP/OCP).
# Adding a new operation = add a member to OperationType + one entry here.
VISITOR_FACTORY = {
    OperationType.EXPLAIN: QueryExplainerVisitor,
    OperationType.OPTIMIZE: QueryOptimizerVisitor,
    OperationType.VALIDATE: QueryValidatorVisitor,
    OperationType.GENERATE_SQL: SQLGeneratorVisitor,
}

analyze_query_use_case = AnalyzeQueryUseCase(visitor_factory=VISITOR_FACTORY)

app = FastAPI(
    title="Query AST Visitor",
    description=(
        "Visitor pattern: ASTNode Elements (SELECT/WHERE/JOIN/...) accept "
        "ConcreteVisitors (explain/optimize/validate/generate_sql) without "
        "the nodes ever knowing the operation's implementation."
    ),
    version="1.0.0",
)


# ── Request/Response models ───────────────────────────────────────────────────


class SelectClause(BaseModel):
    table: str
    columns: list[str] = Field(default_factory=list)


class JoinClause(BaseModel):
    join_type: str
    table: str
    on_condition: str


class LimitClause(BaseModel):
    limit: int
    offset: int = 0


class QueryAnalysisRequest(BaseModel):
    """Raw, framework-agnostic shape of a query the client wants analyzed."""

    select: SelectClause
    where: str | None = None
    joins: list[JoinClause] = Field(default_factory=list)
    group_by: list[str] = Field(default_factory=list)
    order_by: list[tuple[str, str]] = Field(default_factory=list)
    limit: LimitClause | None = None


class AnalysisResponse(BaseModel):
    operation: OperationType
    is_valid: bool
    data: dict[str, object]
    errors: list[str]
    warnings: list[str]


# ── Endpoints ──────────────────────────────────────────────────────────────────


@app.post("/queries/{operation}", response_model=AnalysisResponse)
def analyze_query(
    operation: OperationType, request: QueryAnalysisRequest
) -> AnalysisResponse:
    """Build a QueryAST from the request and run the visitor for `operation`."""
    try:
        report = analyze_query_use_case.execute(
            operation=operation,
            select=request.select.model_dump(),
            where=request.where,
            joins=[join.model_dump() for join in request.joins],
            order_by=request.order_by or None,
            group_by=request.group_by or None,
            limit=request.limit.model_dump() if request.limit else None,
        )
    except UnknownOperationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return AnalysisResponse(
        operation=report.operation,
        is_valid=report.is_valid,
        data=report.data,
        errors=report.errors,
        warnings=report.warnings,
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


__all__ = ["app"]
