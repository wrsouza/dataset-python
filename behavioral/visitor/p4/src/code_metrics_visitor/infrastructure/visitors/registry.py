"""Visitor registry — maps metric names to CodeMetricVisitor factories."""

from __future__ import annotations

from code_metrics_visitor.domain.exceptions import InvalidMetricError
from code_metrics_visitor.domain.interfaces import CodeMetricVisitor
from code_metrics_visitor.infrastructure.visitors.complexity import ComplexityVisitor
from code_metrics_visitor.infrastructure.visitors.doc_coverage import (
    DocCoverageVisitor,
)
from code_metrics_visitor.infrastructure.visitors.line_count import LineCountVisitor

_VISITOR_FACTORIES: dict[str, type[CodeMetricVisitor]] = {
    "lines": LineCountVisitor,
    "complexity": ComplexityVisitor,
    "doc-coverage": DocCoverageVisitor,
}


def get_visitor(name: str) -> CodeMetricVisitor:
    factory = _VISITOR_FACTORIES.get(name.lower())
    if factory is None:
        raise InvalidMetricError(name)
    return factory()


def list_metric_names() -> list[str]:
    return sorted(_VISITOR_FACTORIES)
