"""AnonymizationVisitor: masks each column type so individual values can no
longer be reconstructed, while keeping the shape useful for aggregate analysis."""

from __future__ import annotations

from data_transformation_visitor.domain.interfaces import (
    ColumnVisitor,
    DateColumn,
    NumericColumn,
    TextColumn,
    VisitorResult,
)

_ROUNDING_BUCKET = 10


class AnonymizationVisitor(ColumnVisitor):
    def __init__(self) -> None:
        self._columns: dict[str, object] = {}

    def visit_numeric(self, column: NumericColumn) -> None:
        self._columns[column.name] = [
            round(v / _ROUNDING_BUCKET) * _ROUNDING_BUCKET for v in column.values
        ]

    def visit_text(self, column: TextColumn) -> None:
        self._columns[column.name] = [self._mask(v) for v in column.values]

    def visit_date(self, column: DateColumn) -> None:
        self._columns[column.name] = [v.split("-")[0] for v in column.values]

    @staticmethod
    def _mask(value: str) -> str:
        if not value:
            return value
        return value[0] + "*" * (len(value) - 1)

    @property
    def result(self) -> VisitorResult:
        return VisitorResult(columns=dict(self._columns))
