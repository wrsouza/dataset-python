"""Domain entities for the Analysis Workflow Template."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisReport:
    """Immutable outcome of running an analysis workflow over a dataset."""

    workflow_name: str
    statistics: dict[str, float]
    interpretation: str
    outliers: list[float]
