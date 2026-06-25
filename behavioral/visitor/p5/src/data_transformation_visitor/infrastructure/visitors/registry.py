"""Visitor registry — maps transformation names to ColumnVisitor factories."""

from __future__ import annotations

from data_transformation_visitor.domain.exceptions import InvalidTransformationError
from data_transformation_visitor.domain.interfaces import ColumnVisitor
from data_transformation_visitor.infrastructure.visitors.anonymization import (
    AnonymizationVisitor,
)
from data_transformation_visitor.infrastructure.visitors.normalization import (
    NormalizationVisitor,
)
from data_transformation_visitor.infrastructure.visitors.summary import SummaryVisitor

_VISITOR_FACTORIES: dict[str, type[ColumnVisitor]] = {
    "normalize": NormalizationVisitor,
    "anonymize": AnonymizationVisitor,
    "summary": SummaryVisitor,
}


def get_visitor(name: str) -> ColumnVisitor:
    factory = _VISITOR_FACTORIES.get(name.lower())
    if factory is None:
        raise InvalidTransformationError(name)
    return factory()


def list_transformation_names() -> list[str]:
    return sorted(_VISITOR_FACTORIES)
