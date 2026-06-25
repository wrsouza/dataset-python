"""QueryExplainerVisitor: produces a human-readable description of the query."""

from __future__ import annotations

from query_ast.domain.interfaces import (
    ASTVisitor,
    GroupByNode,
    JoinNode,
    LimitNode,
    OrderByNode,
    SelectNode,
    VisitorResult,
    WhereNode,
)


class QueryExplainerVisitor(ASTVisitor):
    """Concrete Visitor that generates a plain-English query description.

    Useful for documentation, audit logs, and onboarding developers.
    """

    def __init__(self) -> None:
        self._sentences: list[str] = []

    def visit_select(self, node: SelectNode) -> None:
        cols = ", ".join(node.columns) if node.columns else "all columns"
        self._sentences.append(f"Fetch {cols} from the '{node.table}' table.")

    def visit_where(self, node: WhereNode) -> None:
        self._sentences.append(f"Filter rows where {node.condition}.")

    def visit_join(self, node: JoinNode) -> None:
        join_desc = {
            "INNER": "matching rows from",
            "LEFT": "all rows from the left table, with matching rows from",
            "RIGHT": "all rows from the right table, with matching rows from",
            "FULL": "all rows from both tables, including",
        }.get(node.join_type.upper(), "rows from")
        self._sentences.append(
            f"Combine {join_desc} '{node.table}' on {node.on_condition}."
        )

    def visit_order_by(self, node: OrderByNode) -> None:
        parts = [f"{col} ({direction.lower()})" for col, direction in node.columns]
        self._sentences.append(f"Sort results by {', '.join(parts)}.")

    def visit_group_by(self, node: GroupByNode) -> None:
        self._sentences.append(f"Group results by {', '.join(node.columns)}.")

    def visit_limit(self, node: LimitNode) -> None:
        msg = f"Return at most {node.limit} rows."
        if node.offset:
            msg += f" Skip the first {node.offset} rows (pagination offset)."
        self._sentences.append(msg)

    @property
    def result(self) -> VisitorResult:
        explanation = " ".join(self._sentences)
        return VisitorResult(
            data={"explanation": explanation, "steps": self._sentences}
        )


__all__ = ["QueryExplainerVisitor"]
