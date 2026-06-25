"""NormalizationVisitor: min-max scales numbers, trims/lowercases text,
and leaves dates untouched (already ISO-formatted)."""

from __future__ import annotations

from data_transformation_visitor.domain.interfaces import (
    ColumnVisitor,
    DateColumn,
    NumericColumn,
    TextColumn,
    VisitorResult,
)


class NormalizationVisitor(ColumnVisitor):
    def __init__(self) -> None:
        self._columns: dict[str, object] = {}

    def visit_numeric(self, column: NumericColumn) -> None:
        if not column.values:
            self._columns[column.name] = []
            return
        low, high = min(column.values), max(column.values)
        span = high - low
        if span == 0:
            self._columns[column.name] = [0.0 for _ in column.values]
        else:
            self._columns[column.name] = [
                round((v - low) / span, 4) for v in column.values
            ]

    def visit_text(self, column: TextColumn) -> None:
        self._columns[column.name] = [v.strip().lower() for v in column.values]

    def visit_date(self, column: DateColumn) -> None:
        self._columns[column.name] = list(column.values)

    @property
    def result(self) -> VisitorResult:
        return VisitorResult(columns=dict(self._columns))
