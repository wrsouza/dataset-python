"""Unit tests for SummaryVisitor."""

from __future__ import annotations

from data_transformation_visitor.application.structure import traverse
from data_transformation_visitor.domain.interfaces import (
    DateColumn,
    NumericColumn,
    TextColumn,
)
from data_transformation_visitor.infrastructure.visitors.summary import SummaryVisitor


def test_numeric_column_summary() -> None:
    columns = [NumericColumn(name="v", values=[1.0, 2.0, 3.0])]

    result = traverse(columns, SummaryVisitor())

    assert result.columns["v"] == {"count": 3, "mean": 2.0, "min": 1.0, "max": 3.0}


def test_numeric_column_empty_summary() -> None:
    columns = [NumericColumn(name="v", values=[])]

    result = traverse(columns, SummaryVisitor())

    assert result.columns["v"]["count"] == 0


def test_text_column_summary_counts_distinct() -> None:
    columns = [TextColumn(name="n", values=["Ana", "Ana", "Bob"])]

    result = traverse(columns, SummaryVisitor())

    assert result.columns["n"] == {"count": 3, "distinct": 2}


def test_date_column_summary_min_and_max() -> None:
    columns = [DateColumn(name="d", values=["2026-03-20", "2026-01-15"])]

    result = traverse(columns, SummaryVisitor())

    assert result.columns["d"] == {
        "count": 2,
        "earliest": "2026-01-15",
        "latest": "2026-03-20",
    }
