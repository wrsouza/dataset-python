"""AbstractClass for the Template Method pattern — AnalysisWorkflow.

Template Method defines the skeleton of the analysis algorithm in
`run()`. Subclasses override `preprocess()` and `interpret()` —
each workflow cleans and explains the data differently — without
changing the shared statistics/outlier-detection logic.
"""

from __future__ import annotations

import statistics
from abc import ABC, abstractmethod

from analysis_workflow_template.domain.entities import AnalysisReport

_OUTLIER_Z_SCORE_THRESHOLD = 2.0


class AnalysisWorkflow(ABC):
    """AbstractClass: defines the `run()` template method.

    Fixed steps (always run in this order):
        1. preprocess          — abstract, subclass-specific cleaning
        2. compute_statistics  — concrete, shared mean/stdev/min/max
        3. detect_outliers     — concrete, shared z-score check (hook-gated)
        4. interpret           — abstract, subclass-specific explanation

    Hook:
        should_flag_outliers() — returns True (default) to run outlier
                                  detection; subclasses may override to skip it.
    """

    @abstractmethod
    def preprocess(self, values: list[float]) -> list[float]:
        """Clean/normalise the raw dataset before analysis."""

    @abstractmethod
    def interpret(self, stats: dict[str, float]) -> str:
        """Produce a human-readable interpretation of the statistics."""

    @abstractmethod
    def get_name(self) -> str:
        """Return the canonical name of this workflow."""

    # ── Hook ────────────────────────────────────────────────────────────────────

    def should_flag_outliers(self) -> bool:
        """Whether to run outlier detection over the preprocessed data."""
        return True

    # ── Concrete steps ──────────────────────────────────────────────────────────

    def compute_statistics(self, values: list[float]) -> dict[str, float]:
        if not values:
            return {"count": 0, "mean": 0.0, "stdev": 0.0, "min": 0.0, "max": 0.0}
        return {
            "count": float(len(values)),
            "mean": statistics.fmean(values),
            "stdev": statistics.pstdev(values) if len(values) > 1 else 0.0,
            "min": min(values),
            "max": max(values),
        }

    def detect_outliers(
        self, values: list[float], stats: dict[str, float]
    ) -> list[float]:
        mean, stdev = stats["mean"], stats["stdev"]
        if stdev == 0:
            return []
        return [
            v for v in values if abs((v - mean) / stdev) > _OUTLIER_Z_SCORE_THRESHOLD
        ]

    # ── Template Method ─────────────────────────────────────────────────────────

    def run(self, raw_values: list[float]) -> AnalysisReport:
        """Template method — defines the fixed analysis algorithm."""
        values = self.preprocess(raw_values)
        stats = self.compute_statistics(values)
        outliers = (
            self.detect_outliers(values, stats) if self.should_flag_outliers() else []
        )
        interpretation = self.interpret(stats)

        return AnalysisReport(
            workflow_name=self.get_name(),
            statistics=stats,
            interpretation=interpretation,
            outliers=outliers,
        )
