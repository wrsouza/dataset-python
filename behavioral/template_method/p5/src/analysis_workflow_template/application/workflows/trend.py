"""TrendAnalysisWorkflow — ConcreteClass estimating the dataset's direction
over its index (a simple linear-trend approximation)."""

from __future__ import annotations

from analysis_workflow_template.domain.interfaces import AnalysisWorkflow


class TrendAnalysisWorkflow(AnalysisWorkflow):
    def preprocess(self, values: list[float]) -> list[float]:
        # Trend analysis only makes sense over at least 2 points.
        return list(values) if len(values) >= 2 else []

    def compute_statistics(self, values: list[float]) -> dict[str, float]:
        stats = super().compute_statistics(values)
        stats["first"] = values[0] if values else 0.0
        stats["last"] = values[-1] if values else 0.0
        return stats

    def interpret(self, stats: dict[str, float]) -> str:
        if stats["count"] < 2:
            return "Not enough points to estimate a trend."

        slope = self._estimate_slope(stats)
        direction = "upward" if slope > 0 else "downward" if slope < 0 else "flat"
        return f"Trend is {direction} (slope ≈ {slope:.3f} per step)."

    def get_name(self) -> str:
        return "trend"

    # ── Hook override ────────────────────────────────────────────────────────────

    def should_flag_outliers(self) -> bool:
        # A trending series naturally drifts away from its own mean —
        # z-score outlier detection would misfire constantly.
        return False

    # ── Private helper ───────────────────────────────────────────────────────────

    @staticmethod
    def _estimate_slope(stats: dict[str, float]) -> float:
        # Slope between the dataset's first and last point, spread evenly
        # across `count` steps — a coarse but dependency-free trend estimate.
        count = stats["count"]
        if count < 2:
            return 0.0
        return (stats["last"] - stats["first"]) / (count - 1)
