"""Use case orchestrating QueryAST construction and visitor execution."""

from __future__ import annotations

from query_ast.application.structure import QueryAST
from query_ast.domain.entities import AnalysisReport, OperationType
from query_ast.domain.interfaces import (
    ASTNode,
    ASTVisitor,
    GroupByNode,
    JoinNode,
    LimitNode,
    OrderByNode,
    SelectNode,
    WhereNode,
)

VisitorFactory = dict[OperationType, type[ASTVisitor]]


class UnknownOperationError(Exception):
    """Raised when a client requests an operation with no registered visitor."""

    def __init__(self, operation: OperationType) -> None:
        self.operation = operation
        super().__init__(f"No visitor registered for operation '{operation}'.")


class AnalyzeQueryUseCase:
    """Builds a QueryAST from raw clause data and runs the requested visitor.

    Depends only on ASTVisitor (abstraction) via the injected factory map —
    concrete visitors are wired by the caller (composition root), not here.
    """

    def __init__(self, visitor_factory: VisitorFactory) -> None:
        self._visitor_factory = visitor_factory

    def execute(
        self,
        operation: OperationType,
        select: dict[str, object],
        where: str | None = None,
        joins: list[dict[str, object]] | None = None,
        order_by: list[tuple[str, str]] | None = None,
        group_by: list[str] | None = None,
        limit: dict[str, int] | None = None,
    ) -> AnalysisReport:
        """Assemble the AST nodes, dispatch the chosen visitor, return a report."""
        visitor_cls = self._visitor_factory.get(operation)
        if visitor_cls is None:
            raise UnknownOperationError(operation)

        ast = self._build_ast(select, where, joins, order_by, group_by, limit)
        visitor = visitor_cls()
        result = ast.accept_visitor(visitor)

        return AnalysisReport(
            operation=operation,
            is_valid=result.is_valid,
            data=result.data,
            errors=result.errors,
            warnings=result.warnings,
        )

    @staticmethod
    def _build_ast(
        select: dict[str, object],
        where: str | None,
        joins: list[dict[str, object]] | None,
        order_by: list[tuple[str, str]] | None,
        group_by: list[str] | None,
        limit: dict[str, int] | None,
    ) -> QueryAST:
        """Translate plain request data into the AST's Element nodes."""
        raw_columns = select.get("columns", [])
        columns = list(raw_columns) if isinstance(raw_columns, list) else []
        nodes: list[ASTNode] = [SelectNode(columns=columns, table=str(select["table"]))]
        if where:
            nodes.append(WhereNode(condition=where))
        for join in joins or []:
            nodes.append(
                JoinNode(
                    join_type=str(join["join_type"]),
                    table=str(join["table"]),
                    on_condition=str(join["on_condition"]),
                )
            )
        if group_by:
            nodes.append(GroupByNode(columns=group_by))
        if order_by:
            nodes.append(OrderByNode(columns=order_by))
        if limit:
            nodes.append(
                LimitNode(limit=int(limit["limit"]), offset=int(limit.get("offset", 0)))
            )
        return QueryAST(nodes=nodes)


__all__ = ["AnalyzeQueryUseCase", "UnknownOperationError", "VisitorFactory"]
