"""Application use cases for the Chart Visualization Factory.

The Client role in the Abstract Factory pattern lives here.
Use cases depend only on ChartFactory (abstraction) — never on concrete factories.
This demonstrates the Dependency Inversion Principle.
"""
from __future__ import annotations

import pandas as pd

from chart_factory.domain.entities import ChartRenderResult, SalesDataset
from chart_factory.domain.interfaces import ChartFactory


class RenderChartFamilyUseCase:
    """Client that uses ChartFactory to render a full set of charts.

    DIP: receives factory via constructor — does not import any concrete class.
    SRP: single responsibility — render the three chart types for a given dataset.
    """

    def __init__(self, factory: ChartFactory) -> None:
        self._factory = factory

    def execute(self, dataset: SalesDataset) -> list[ChartRenderResult]:
        """Render line, bar, and pie charts for the given dataset.

        Returns one ChartRenderResult per chart type, preserving insertion order.
        The concrete chart type (plotly Figure, matplotlib Figure, altair Chart)
        is opaque to the caller — only the metadata fields are library-agnostic.
        """
        data: pd.DataFrame = dataset.to_dataframe()

        line_chart = self._factory.create_line_chart()
        bar_chart = self._factory.create_bar_chart()
        pie_chart = self._factory.create_pie_chart()

        return [
            ChartRenderResult(
                library_name=line_chart.get_library_name(),
                chart_type="line",
                figure=line_chart.render(data),
            ),
            ChartRenderResult(
                library_name=bar_chart.get_library_name(),
                chart_type="bar",
                figure=bar_chart.render(data),
            ),
            ChartRenderResult(
                library_name=pie_chart.get_library_name(),
                chart_type="pie",
                figure=pie_chart.render(data),
            ),
        ]


class GetAvailableLibrariesUseCase:
    """Return the library names of a set of factories.

    Used by the Streamlit sidebar to populate the selectbox without
    importing concrete factory classes.
    """

    def __init__(self, factories: dict[str, ChartFactory]) -> None:
        # Keys are display labels; values are concrete factories.
        self._factories = factories

    def execute(self) -> list[str]:
        """Return the list of library display names."""
        return list(self._factories.keys())

    def get_factory(self, library_name: str) -> ChartFactory:
        """Retrieve a factory by its display label.

        Raises KeyError when the label is not registered, matching the
        same early-return / specific-exception style used across the dataset.
        """
        if library_name not in self._factories:
            supported = ", ".join(self._factories.keys())
            raise KeyError(
                f"Unknown library '{library_name}'. Available: {supported}"
            )
        return self._factories[library_name]
