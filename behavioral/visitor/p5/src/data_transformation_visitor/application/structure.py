"""Traversal helper for applying a visitor to every column in a dataset."""

from __future__ import annotations

from data_transformation_visitor.domain.interfaces import (
    ColumnVisitor,
    DataColumn,
    VisitorResult,
)


def traverse(columns: list[DataColumn], visitor: ColumnVisitor) -> VisitorResult:
    """Visit every column and return the visitor's accumulated result."""
    for column in columns:
        column.accept(visitor)
    return visitor.result
