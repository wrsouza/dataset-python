"""Unit tests for the visitor registry and JSON-to-domain structure builder."""

from __future__ import annotations

import pytest

from code_metrics_visitor.application.structure import build_module
from code_metrics_visitor.domain.exceptions import InvalidMetricError
from code_metrics_visitor.infrastructure.visitors.line_count import LineCountVisitor
from code_metrics_visitor.infrastructure.visitors.registry import (
    get_visitor,
    list_metric_names,
)


def test_get_visitor_resolves_lines() -> None:
    assert isinstance(get_visitor("lines"), LineCountVisitor)


def test_get_visitor_is_case_insensitive() -> None:
    assert get_visitor("COMPLEXITY").__class__.__name__ == "ComplexityVisitor"


def test_get_visitor_raises_for_unknown_metric() -> None:
    with pytest.raises(InvalidMetricError):
        get_visitor("unknown")


def test_list_metric_names() -> None:
    assert list_metric_names() == ["complexity", "doc-coverage", "lines"]


def test_build_module_parses_nested_structure() -> None:
    module = build_module(
        {
            "name": "m",
            "functions": [
                {"name": "f", "line_count": 5, "branch_count": 1, "has_docstring": True}
            ],
            "classes": [
                {
                    "name": "C",
                    "has_docstring": False,
                    "methods": [{"name": "m1", "line_count": 3}],
                }
            ],
        }
    )

    assert module.name == "m"
    assert module.functions[0].name == "f"
    assert module.classes[0].methods[0].name == "m1"
    assert module.classes[0].methods[0].branch_count == 0


def test_build_module_defaults_for_missing_keys() -> None:
    module = build_module({"name": "empty"})

    assert module.functions == []
    assert module.classes == []
