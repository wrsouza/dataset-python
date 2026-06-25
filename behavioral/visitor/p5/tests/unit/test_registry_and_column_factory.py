"""Unit tests for the visitor registry and column factory."""

from __future__ import annotations

import pytest

from data_transformation_visitor.application.column_factory import (
    build_column,
    build_columns,
)
from data_transformation_visitor.domain.exceptions import (
    InvalidColumnTypeError,
    InvalidTransformationError,
)
from data_transformation_visitor.domain.interfaces import NumericColumn, TextColumn
from data_transformation_visitor.infrastructure.visitors.normalization import (
    NormalizationVisitor,
)
from data_transformation_visitor.infrastructure.visitors.registry import (
    get_visitor,
    list_transformation_names,
)


def test_get_visitor_resolves_normalize() -> None:
    assert isinstance(get_visitor("normalize"), NormalizationVisitor)


def test_get_visitor_is_case_insensitive() -> None:
    assert get_visitor("ANONYMIZE").__class__.__name__ == "AnonymizationVisitor"


def test_get_visitor_raises_for_unknown_transformation() -> None:
    with pytest.raises(InvalidTransformationError):
        get_visitor("unknown")


def test_list_transformation_names() -> None:
    assert list_transformation_names() == ["anonymize", "normalize", "summary"]


def test_build_column_numeric() -> None:
    column = build_column({"type": "numeric", "name": "v", "values": [1.0]})

    assert isinstance(column, NumericColumn)


def test_build_column_text() -> None:
    column = build_column({"type": "text", "name": "n", "values": ["a"]})

    assert isinstance(column, TextColumn)


def test_build_column_raises_for_unknown_type() -> None:
    with pytest.raises(InvalidColumnTypeError):
        build_column({"type": "unknown"})


def test_build_columns_builds_a_list() -> None:
    columns = build_columns(
        [
            {"type": "numeric", "name": "v", "values": [1.0]},
            {"type": "text", "name": "n", "values": ["a"]},
        ]
    )

    assert len(columns) == 2
