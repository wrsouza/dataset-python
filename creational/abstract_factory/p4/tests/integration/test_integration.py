"""Integration tests for P4 — end-to-end rendering with real chart libraries.

These tests exercise the full stack: factory → product → render().
No external services required (all chart libraries are pure-Python).
"""
from __future__ import annotations

import altair as alt
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from chart_factory.application.use_cases import RenderChartFamilyUseCase
from chart_factory.domain.entities import SalesDataset
from chart_factory.infrastructure.factories import (
    AltairChartFactory,
    MatplotlibChartFactory,
    PlotlyChartFactory,
)


class TestPlotlyIntegration:
    """Full rendering pipeline using Plotly."""

    def test_full_render_pipeline_produces_valid_plotly_figures(self) -> None:
        dataset = SalesDataset.build_synthetic()
        factory = PlotlyChartFactory()
        use_case = RenderChartFamilyUseCase(factory=factory)
        results = use_case.execute(dataset)

        for result in results:
            assert isinstance(result.figure, go.Figure)
            # A rendered Plotly figure always has at least one trace
            assert len(result.figure.data) >= 1

    def test_plotly_line_chart_has_one_trace_per_product(self) -> None:
        dataset = SalesDataset.build_synthetic()
        fig = PlotlyChartFactory().create_line_chart().render(dataset.to_dataframe())
        # 3 products → 3 line traces
        assert len(fig.data) == 3


class TestMatplotlibIntegration:
    """Full rendering pipeline using Matplotlib."""

    def test_full_render_pipeline_produces_matplotlib_figures(self) -> None:
        dataset = SalesDataset.build_synthetic()
        factory = MatplotlibChartFactory()
        use_case = RenderChartFamilyUseCase(factory=factory)
        results = use_case.execute(dataset)

        for result in results:
            assert isinstance(result.figure, plt.Figure)
            plt.close(result.figure)

    def test_matplotlib_figures_have_axes(self) -> None:
        dataset = SalesDataset.build_synthetic()
        factory = MatplotlibChartFactory()
        fig = factory.create_line_chart().render(dataset.to_dataframe())
        assert len(fig.axes) > 0
        plt.close(fig)


class TestAltairIntegration:
    """Full rendering pipeline using Altair."""

    def test_full_render_pipeline_produces_altair_charts(self) -> None:
        dataset = SalesDataset.build_synthetic()
        factory = AltairChartFactory()
        use_case = RenderChartFamilyUseCase(factory=factory)
        results = use_case.execute(dataset)

        for result in results:
            assert isinstance(result.figure, alt.Chart)

    def test_altair_charts_can_be_serialised_to_dict(self) -> None:
        """Altair charts must be JSON-serialisable for Vega-Lite rendering."""
        dataset = SalesDataset.build_synthetic()
        factory = AltairChartFactory()
        for chart in [
            factory.create_line_chart().render(dataset.to_dataframe()),
            factory.create_bar_chart().render(dataset.to_dataframe()),
            factory.create_pie_chart().render(dataset.to_dataframe()),
        ]:
            spec = chart.to_dict()
            assert "mark" in spec or "encoding" in spec or "layer" in spec or "spec" in spec


class TestCrossLibraryConsistency:
    """Verify that all families render the same number of charts."""

    def test_all_factories_produce_three_chart_types(self) -> None:
        dataset = SalesDataset.build_synthetic()
        for factory_cls in [PlotlyChartFactory, MatplotlibChartFactory, AltairChartFactory]:
            use_case = RenderChartFamilyUseCase(factory=factory_cls())
            results = use_case.execute(dataset)
            assert len(results) == 3, f"{factory_cls.__name__} must produce 3 charts"

    def test_all_factories_cover_same_chart_types(self) -> None:
        dataset = SalesDataset.build_synthetic()
        expected_types = {"line", "bar", "pie"}
        for factory_cls in [PlotlyChartFactory, MatplotlibChartFactory, AltairChartFactory]:
            use_case = RenderChartFamilyUseCase(factory=factory_cls())
            results = use_case.execute(dataset)
            assert {r.chart_type for r in results} == expected_types
