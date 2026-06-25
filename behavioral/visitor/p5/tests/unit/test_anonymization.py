"""Unit tests for AnonymizationVisitor."""

from __future__ import annotations

from data_transformation_visitor.application.structure import traverse
from data_transformation_visitor.domain.interfaces import (
    DateColumn,
    NumericColumn,
    TextColumn,
)
from data_transformation_visitor.infrastructure.visitors.anonymization import (
    AnonymizationVisitor,
)


def test_numeric_column_rounded_to_nearest_bucket() -> None:
    columns = [NumericColumn(name="v", values=[12.0, 27.0])]

    result = traverse(columns, AnonymizationVisitor())

    assert result.columns["v"] == [10, 30]


def test_text_column_masked_except_first_char() -> None:
    columns = [TextColumn(name="n", values=["Ana", ""])]

    result = traverse(columns, AnonymizationVisitor())

    assert result.columns["n"] == ["A**", ""]


def test_date_column_keeps_only_year() -> None:
    columns = [DateColumn(name="d", values=["2026-03-20"])]

    result = traverse(columns, AnonymizationVisitor())

    assert result.columns["d"] == ["2026"]
