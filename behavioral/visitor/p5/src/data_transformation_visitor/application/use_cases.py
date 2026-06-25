"""Application use case for the Data Transformation Visitor system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from data_transformation_visitor.application.column_factory import build_columns
from data_transformation_visitor.application.structure import traverse
from data_transformation_visitor.domain.interfaces import VisitorResult
from data_transformation_visitor.infrastructure.visitors.registry import get_visitor


@dataclass
class TransformDatasetInput:
    transformation_name: str
    columns: list[dict[str, Any]]


class TransformDatasetUseCase:
    def execute(self, data: TransformDatasetInput) -> VisitorResult:
        visitor = get_visitor(data.transformation_name)
        columns = build_columns(data.columns)
        return traverse(columns, visitor)
