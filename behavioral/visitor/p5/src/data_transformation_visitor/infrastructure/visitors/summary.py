"""SummaryVisitor: computes type-appropriate aggregate stats per column."""

from __future__ import annotations

import statistics

from data_transformation_visitor.domain.interfaces import (
    ColumnVisitor,
    DateColumn,
    NumericColumn,
    TextColumn,
    VisitorResult,
)


class SummaryVisitor(ColumnVisitor):
    def __init__(self) -> None:
        self._columns: dict[str, object] = {}

    def visit_numeric(self, column: NumericColumn) -> None:
        if not column.values:
            self._columns[column.name] = {
                "count": 0,
                "mean": 0.0,
                "min": 0.0,
                "max": 0.0,
            }
            return
        self._columns[column.name] = {
            "count": len(column.values),
            "mean": round(statistics.fmean(column.values), 4),
            "min": min(column.values),
            "max": max(column.values),
        }

    def visit_text(self, column: TextColumn) -> None:
        self._columns[column.name] = {
            "count": len(column.values),
            "distinct": len(set(column.values)),
        }

    def visit_date(self, column: DateColumn) -> None:
        self._columns[column.name] = {
            "count": len(column.values),
            "earliest": min(column.values) if column.values else None,
            "latest": max(column.values) if column.values else None,
        }

    @property
    def result(self) -> VisitorResult:
        return VisitorResult(columns=dict(self._columns))
