"""Application use case for the Code Metrics Visitor system."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from code_metrics_visitor.application.structure import build_module, traverse
from code_metrics_visitor.domain.interfaces import VisitorResult
from code_metrics_visitor.infrastructure.visitors.registry import get_visitor


@dataclass
class AnalyzeModuleInput:
    module_path: Path
    metric_name: str


class AnalyzeModuleUseCase:
    def execute(self, data: AnalyzeModuleInput) -> VisitorResult:
        payload = json.loads(data.module_path.read_text())
        module = build_module(payload)
        visitor = get_visitor(data.metric_name)
        return traverse(module, visitor)
