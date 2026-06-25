"""Unit tests for NormalizationVisitor."""

from __future__ import annotations

from data_transformation_visitor.application.structure import traverse
from data_transformation_visitor.domain.interfaces import (
    DateColumn,
    NumericColumn,
    TextColumn,
)
from data_transformation_visitor.infrastructure.visitors.normalization import (
    NormalizationVisitor,
)


def test_numeric_column_min_max_scaled() -> None:
    columns = [NumericColumn(name="v", values=[0.0, 5.0, 10.0])]

    result = traverse(columns, NormalizationVisitor())

    assert result.columns["v"] == [0.0, 0.5, 1.0]


def test_numeric_column_with_no_spread() -> None:
    columns = [NumericColumn(name="v", values=[5.0, 5.0])]

    result = traverse(columns, NormalizationVisitor())

    assert result.columns["v"] == [0.0, 0.0]


def test_numeric_column_empty() -> None:
    columns = [NumericColumn(name="v", values=[])]

    result = traverse(columns, NormalizationVisitor())

    assert result.columns["v"] == []


def test_text_column_trimmed_and_lowercased() -> None:
    columns = [TextColumn(name="n", values=[" Ana ", "BOB"])]

    result = traverse(columns, NormalizationVisitor())

    assert result.columns["n"] == ["ana", "bob"]


def test_date_column_unchanged() -> None:
    columns = [DateColumn(name="d", values=["2026-01-15"])]

    result = traverse(columns, NormalizationVisitor())

    assert result.columns["d"] == ["2026-01-15"]
