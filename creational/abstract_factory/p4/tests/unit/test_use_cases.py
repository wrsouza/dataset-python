"""Unit tests for the Chart Visualization Factory use cases.

No external services are required — all tests use in-memory factories.
Tests verify pattern structure, SOLID compliance, and rendering contracts.
"""
from __future__ import annotations

import altair as alt
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pytest

from chart_factory.application.use_cases import (
    GetAvailableLibrariesUseCase,
    RenderChartFamilyUseCase,
)
from chart_factory.domain.entities import ChartRenderResult, SalesDataset
from chart_factory.infrastructure.factories import (
    CHART_FACTORIES,
    AltairChartFactory,
    MatplotlibChartFactory,
    PlotlyChartFactory,
    get_factory_for_library,
)


class TestSalesDataset:
    """Tests for the SalesDataset domain entity."""

    def test_build_synthetic_produces_records(self) -> None:
        dataset = SalesDataset.build_synthetic()
        assert len(dataset.records) == 18  # 3 products × 6 months

    def test_to_dataframe_has_expected_columns(self, sales_dataset: SalesDataset) -> None:
        df = sales_dataset.to_dataframe()
        assert set(df.columns) == {"month", "product", "revenue", "units_sold"}

    def test_to_dataframe_row_count_matches_records(self, sales_dataset: SalesDataset) -> None:
        df = sales_dataset.to_dataframe()
        assert len(df) == len(sales_dataset.records)

    def test_revenue_values_are_positive(self, sales_dataset: SalesDataset) -> None:
        df = sales_dataset.to_dataframe()
        assert (df["revenue"] > 0).all()


class TestPlotlyChartFactory:
    """Tests for the PlotlyChartFactory concrete family."""

    def test_get_library_name(self, plotly_factory: PlotlyChartFactory) -> None:
        assert plotly_factory.get_library_name() == "Plotly"

    def test_create_line_chart_returns_correct_library(
        self, plotly_factory: PlotlyChartFactory
    ) -> None:
        chart = plotly_factory.create_line_chart()
        assert chart.get_library_name() == "plotly"

    def test_create_bar_chart_returns_correct_library(
        self, plotly_factory: PlotlyChartFactory
    ) -> None:
        assert plotly_factory.create_bar_chart().get_library_name() == "plotly"

    def test_create_pie_chart_returns_correct_library(
        self, plotly_factory: PlotlyChartFactory
    ) -> None:
        assert plotly_factory.create_pie_chart().get_library_name() == "plotly"

    def test_line_chart_render_returns_plotly_figure(
        self, plotly_factory: PlotlyChartFactory, sales_dataset: SalesDataset
    ) -> None:
        fig = plotly_factory.create_line_chart().render(sales_dataset.to_dataframe())
        assert isinstance(fig, go.Figure)

    def test_bar_chart_render_returns_plotly_figure(
        self, plotly_factory: PlotlyChartFactory, sales_dataset: SalesDataset
    ) -> None:
        fig = plotly_factory.create_bar_chart().render(sales_dataset.to_dataframe())
        assert isinstance(fig, go.Figure)

    def test_pie_chart_render_returns_plotly_figure(
        self, plotly_factory: PlotlyChartFactory, sales_dataset: SalesDataset
    ) -> None:
        fig = plotly_factory.create_pie_chart().render(sales_dataset.to_dataframe())
        assert isinstance(fig, go.Figure)


class TestMatplotlibChartFactory:
    """Tests for the MatplotlibChartFactory concrete family."""

    def test_get_library_name(self, matplotlib_factory: MatplotlibChartFactory) -> None:
        assert matplotlib_factory.get_library_name() == "Matplotlib"

    def test_all_products_return_matplotlib_library_name(
        self, matplotlib_factory: MatplotlibChartFactory
    ) -> None:
        for product in [
            matplotlib_factory.create_line_chart(),
            matplotlib_factory.create_bar_chart(),
            matplotlib_factory.create_pie_chart(),
        ]:
            assert product.get_library_name() == "matplotlib"

    def test_line_chart_render_returns_matplotlib_figure(
        self, matplotlib_factory: MatplotlibChartFactory, sales_dataset: SalesDataset
    ) -> None:
        fig = matplotlib_factory.create_line_chart().render(sales_dataset.to_dataframe())
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_bar_chart_render_returns_matplotlib_figure(
        self, matplotlib_factory: MatplotlibChartFactory, sales_dataset: SalesDataset
    ) -> None:
        fig = matplotlib_factory.create_bar_chart().render(sales_dataset.to_dataframe())
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_pie_chart_render_returns_matplotlib_figure(
        self, matplotlib_factory: MatplotlibChartFactory, sales_dataset: SalesDataset
    ) -> None:
        fig = matplotlib_factory.create_pie_chart().render(sales_dataset.to_dataframe())
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestAltairChartFactory:
    """Tests for the AltairChartFactory concrete family."""

    def test_get_library_name(self, altair_factory: AltairChartFactory) -> None:
        assert altair_factory.get_library_name() == "Altair"

    def test_all_products_return_altair_library_name(
        self, altair_factory: AltairChartFactory
    ) -> None:
        for product in [
            altair_factory.create_line_chart(),
            altair_factory.create_bar_chart(),
            altair_factory.create_pie_chart(),
        ]:
            assert product.get_library_name() == "altair"

    def test_line_chart_render_returns_altair_chart(
        self, altair_factory: AltairChartFactory, sales_dataset: SalesDataset
    ) -> None:
        chart = altair_factory.create_line_chart().render(sales_dataset.to_dataframe())
        assert isinstance(chart, alt.Chart)

    def test_bar_chart_render_returns_altair_chart(
        self, altair_factory: AltairChartFactory, sales_dataset: SalesDataset
    ) -> None:
        chart = altair_factory.create_bar_chart().render(sales_dataset.to_dataframe())
        assert isinstance(chart, alt.Chart)

    def test_pie_chart_render_returns_altair_chart(
        self, altair_factory: AltairChartFactory, sales_dataset: SalesDataset
    ) -> None:
        chart = altair_factory.create_pie_chart().render(sales_dataset.to_dataframe())
        assert isinstance(chart, alt.Chart)


class TestRenderChartFamilyUseCase:
    """Tests for the Client use case (pattern role: Client)."""

    def test_execute_returns_three_results(
        self,
        plotly_factory: PlotlyChartFactory,
        sales_dataset: SalesDataset,
    ) -> None:
        use_case = RenderChartFamilyUseCase(factory=plotly_factory)
        results = use_case.execute(sales_dataset)
        assert len(results) == 3

    def test_execute_returns_chart_render_results(
        self,
        matplotlib_factory: MatplotlibChartFactory,
        sales_dataset: SalesDataset,
    ) -> None:
        use_case = RenderChartFamilyUseCase(factory=matplotlib_factory)
        results = use_case.execute(sales_dataset)
        assert all(isinstance(r, ChartRenderResult) for r in results)

    def test_execute_chart_types_are_line_bar_pie(
        self,
        altair_factory: AltairChartFactory,
        sales_dataset: SalesDataset,
    ) -> None:
        use_case = RenderChartFamilyUseCase(factory=altair_factory)
        results = use_case.execute(sales_dataset)
        chart_types = [r.chart_type for r in results]
        assert chart_types == ["line", "bar", "pie"]

    def test_dip_use_case_works_with_any_factory(
        self, sales_dataset: SalesDataset
    ) -> None:
        """DIP: the use case is unchanged regardless of which ConcreteFactory is injected."""
        for factory in [PlotlyChartFactory(), MatplotlibChartFactory(), AltairChartFactory()]:
            use_case = RenderChartFamilyUseCase(factory=factory)
            results = use_case.execute(sales_dataset)
            assert len(results) == 3
            assert all(r.library_name == factory.get_library_name().lower() for r in results)

    def test_result_library_name_matches_factory(
        self, plotly_factory: PlotlyChartFactory, sales_dataset: SalesDataset
    ) -> None:
        use_case = RenderChartFamilyUseCase(factory=plotly_factory)
        results = use_case.execute(sales_dataset)
        assert all(r.library_name == "plotly" for r in results)


class TestGetAvailableLibrariesUseCase:
    """Tests for the library discovery use case."""

    def test_execute_returns_all_registered_libraries(self) -> None:
        use_case = GetAvailableLibrariesUseCase(factories=CHART_FACTORIES)
        libs = use_case.execute()
        assert set(libs) == {"Plotly", "Matplotlib", "Altair"}

    def test_get_factory_returns_correct_type(self) -> None:
        use_case = GetAvailableLibrariesUseCase(factories=CHART_FACTORIES)
        factory = use_case.get_factory("Plotly")
        assert isinstance(factory, PlotlyChartFactory)

    def test_get_factory_raises_for_unknown_library(self) -> None:
        use_case = GetAvailableLibrariesUseCase(factories=CHART_FACTORIES)
        with pytest.raises(KeyError, match="Unknown library"):
            use_case.get_factory("D3")


class TestFactoryRegistry:
    """Tests for the OCP-compliant factory registry."""

    @pytest.mark.parametrize("library", ["Plotly", "Matplotlib", "Altair"])
    def test_get_factory_for_library_returns_correct_factory(self, library: str) -> None:
        factory = get_factory_for_library(library)
        assert factory.get_library_name() == library

    def test_unsupported_library_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Unsupported library"):
            get_factory_for_library("Bokeh")

    def test_ocp_factories_produce_independent_products(self) -> None:
        """OCP: products from different families are independent implementations."""
        plotly_lib = get_factory_for_library("Plotly").create_line_chart().get_library_name()
        mpl_lib = get_factory_for_library("Matplotlib").create_line_chart().get_library_name()
        alt_lib = get_factory_for_library("Altair").create_line_chart().get_library_name()
        assert len({plotly_lib, mpl_lib, alt_lib}) == 3  # all different
