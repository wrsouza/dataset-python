"""Concrete Factories and Concrete Products for the Chart Visualization Factory.

Three library families are provided: Plotly, Matplotlib, and Altair.
Each family produces LineChart, BarChart, and PieChart products that are
visually consistent within the library but independently implemented.

OCP: adding a new library (e.g. Bokeh) requires only a new set of concrete
     classes appended here — no existing factory, use case or UI code changes.
"""
from __future__ import annotations

from typing import Any

import altair as alt
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from chart_factory.domain.interfaces import BarChart, ChartFactory, LineChart, PieChart

# Use non-interactive backend so matplotlib does not open a GUI window.
matplotlib.use("Agg")


# ── Plotly Concrete Products ───────────────────────────────────────────────────


class PlotlyLineChart(LineChart):
    """ConcreteProduct: line chart rendered with Plotly Express."""

    def render(self, data: pd.DataFrame) -> go.Figure:
        fig = px.line(
            data,
            x="month",
            y="revenue",
            color="product",
            title="Monthly Revenue (Plotly)",
            markers=True,
            labels={"revenue": "Revenue (USD)", "month": "Month"},
        )
        fig.update_layout(legend_title_text="Product")
        return fig

    def get_library_name(self) -> str:
        return "plotly"


class PlotlyBarChart(BarChart):
    """ConcreteProduct: bar chart rendered with Plotly Express."""

    def render(self, data: pd.DataFrame) -> go.Figure:
        fig = px.bar(
            data,
            x="month",
            y="units_sold",
            color="product",
            barmode="group",
            title="Units Sold per Month (Plotly)",
            labels={"units_sold": "Units Sold", "month": "Month"},
        )
        return fig

    def get_library_name(self) -> str:
        return "plotly"


class PlotlyPieChart(PieChart):
    """ConcreteProduct: pie chart rendered with Plotly Express."""

    def render(self, data: pd.DataFrame) -> go.Figure:
        totals = data.groupby("product")["revenue"].sum().reset_index()
        fig = px.pie(
            totals,
            names="product",
            values="revenue",
            title="Revenue Share by Product (Plotly)",
            hole=0.35,  # donut style
        )
        return fig

    def get_library_name(self) -> str:
        return "plotly"


# ── Matplotlib Concrete Products ───────────────────────────────────────────────


class MatplotlibLineChart(LineChart):
    """ConcreteProduct: line chart rendered with Matplotlib."""

    def render(self, data: pd.DataFrame) -> Any:
        fig, ax = plt.subplots(figsize=(8, 4))
        for product, group in data.groupby("product"):
            ax.plot(group["month"], group["revenue"], marker="o", label=product)
        ax.set_title("Monthly Revenue (Matplotlib)")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue (USD)")
        ax.legend(title="Product")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        fig.tight_layout()
        return fig

    def get_library_name(self) -> str:
        return "matplotlib"


class MatplotlibBarChart(BarChart):
    """ConcreteProduct: grouped bar chart rendered with Matplotlib."""

    def render(self, data: pd.DataFrame) -> Any:
        products = data["product"].unique()
        months = data["month"].unique()
        bar_width = 0.25
        x = range(len(months))

        fig, ax = plt.subplots(figsize=(8, 4))
        for i, product in enumerate(products):
            subset = data[data["product"] == product]
            offsets = [xi + i * bar_width for xi in x]
            ax.bar(offsets, subset["units_sold"], width=bar_width, label=product)

        ax.set_xticks([xi + bar_width for xi in x])
        ax.set_xticklabels(months)
        ax.set_title("Units Sold per Month (Matplotlib)")
        ax.set_xlabel("Month")
        ax.set_ylabel("Units Sold")
        ax.legend(title="Product")
        fig.tight_layout()
        return fig

    def get_library_name(self) -> str:
        return "matplotlib"


class MatplotlibPieChart(PieChart):
    """ConcreteProduct: pie chart rendered with Matplotlib."""

    def render(self, data: pd.DataFrame) -> Any:
        totals = data.groupby("product")["revenue"].sum()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(
            totals.values,
            labels=totals.index,
            autopct="%1.1f%%",
            startangle=140,
            wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        )
        ax.set_title("Revenue Share by Product (Matplotlib)")
        return fig

    def get_library_name(self) -> str:
        return "matplotlib"


# ── Altair Concrete Products ───────────────────────────────────────────────────


class AltairLineChart(LineChart):
    """ConcreteProduct: line chart rendered with Altair (Vega-Lite)."""

    def render(self, data: pd.DataFrame) -> alt.Chart:
        chart = (
            alt.Chart(data)
            .mark_line(point=True)
            .encode(
                x=alt.X("month:N", title="Month", sort=None),
                y=alt.Y("revenue:Q", title="Revenue (USD)"),
                color=alt.Color("product:N", title="Product"),
                tooltip=["month", "product", "revenue"],
            )
            .properties(title="Monthly Revenue (Altair)", width=600, height=300)
        )
        return chart

    def get_library_name(self) -> str:
        return "altair"


class AltairBarChart(BarChart):
    """ConcreteProduct: grouped bar chart rendered with Altair (Vega-Lite)."""

    def render(self, data: pd.DataFrame) -> alt.Chart:
        chart = (
            alt.Chart(data)
            .mark_bar()
            .encode(
                x=alt.X("month:N", title="Month", sort=None),
                y=alt.Y("units_sold:Q", title="Units Sold"),
                color=alt.Color("product:N", title="Product"),
                xOffset="product:N",
                tooltip=["month", "product", "units_sold"],
            )
            .properties(title="Units Sold per Month (Altair)", width=600, height=300)
        )
        return chart

    def get_library_name(self) -> str:
        return "altair"


class AltairPieChart(PieChart):
    """ConcreteProduct: pie / arc chart rendered with Altair (Vega-Lite).

    Altair uses arc marks for pie-style charts; the pattern role is fulfilled
    even though the API differs from matplotlib/plotly.
    """

    def render(self, data: pd.DataFrame) -> alt.Chart:
        totals = data.groupby("product")["revenue"].sum().reset_index()
        chart = (
            alt.Chart(totals)
            .mark_arc(outerRadius=120, innerRadius=50)
            .encode(
                theta=alt.Theta("revenue:Q"),
                color=alt.Color("product:N", title="Product"),
                tooltip=["product", "revenue"],
            )
            .properties(title="Revenue Share by Product (Altair)", width=300, height=300)
        )
        return chart

    def get_library_name(self) -> str:
        return "altair"


# ── Concrete Factories ─────────────────────────────────────────────────────────


class PlotlyChartFactory(ChartFactory):
    """ConcreteFactory: creates the Plotly chart family."""

    def create_line_chart(self) -> PlotlyLineChart:
        return PlotlyLineChart()

    def create_bar_chart(self) -> PlotlyBarChart:
        return PlotlyBarChart()

    def create_pie_chart(self) -> PlotlyPieChart:
        return PlotlyPieChart()

    def get_library_name(self) -> str:
        return "Plotly"


class MatplotlibChartFactory(ChartFactory):
    """ConcreteFactory: creates the Matplotlib chart family."""

    def create_line_chart(self) -> MatplotlibLineChart:
        return MatplotlibLineChart()

    def create_bar_chart(self) -> MatplotlibBarChart:
        return MatplotlibBarChart()

    def create_pie_chart(self) -> MatplotlibPieChart:
        return MatplotlibPieChart()

    def get_library_name(self) -> str:
        return "Matplotlib"


class AltairChartFactory(ChartFactory):
    """ConcreteFactory: creates the Altair (Vega-Lite) chart family."""

    def create_line_chart(self) -> AltairLineChart:
        return AltairLineChart()

    def create_bar_chart(self) -> AltairBarChart:
        return AltairBarChart()

    def create_pie_chart(self) -> AltairPieChart:
        return AltairPieChart()

    def get_library_name(self) -> str:
        return "Altair"


# ── Factory Registry ───────────────────────────────────────────────────────────

CHART_FACTORIES: dict[str, ChartFactory] = {
    "Plotly": PlotlyChartFactory(),
    "Matplotlib": MatplotlibChartFactory(),
    "Altair": AltairChartFactory(),
}


def get_factory_for_library(library: str) -> ChartFactory:
    """Return the appropriate ChartFactory for the given library name.

    OCP: to add a new library, register it in CHART_FACTORIES.
    No conditional branching is scattered across the codebase.
    """
    factory = CHART_FACTORIES.get(library)
    if factory is None:
        supported = ", ".join(CHART_FACTORIES.keys())
        raise ValueError(f"Unsupported library '{library}'. Supported: {supported}")
    return factory
