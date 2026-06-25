"""DescriptiveAnalysisWorkflow — ConcreteClass summarising a dataset as-is."""

from __future__ import annotations

from analysis_workflow_template.domain.interfaces import AnalysisWorkflow


class DescriptiveAnalysisWorkflow(AnalysisWorkflow):
    def preprocess(self, values: list[float]) -> list[float]:
        return list(values)

    def interpret(self, stats: dict[str, float]) -> str:
        if stats["count"] == 0:
            return "No data to describe."
        return (
            f"Dataset has {int(stats['count'])} points, averaging "
            f"{stats['mean']:.2f} (stdev {stats['stdev']:.2f}), "
            f"ranging from {stats['min']:.2f} to {stats['max']:.2f}."
        )

    def get_name(self) -> str:
        return "descriptive"
