"""Streamlit application — Chart Visualization Factory.

Composition root: this is the only file that imports concrete classes.
The Streamlit UI depends on ChartFactory (abstraction) via use cases.

Run:
    streamlit run src/chart_factory/app.py
"""
from __future__ import annotations

import altair as alt
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st

from chart_factory.application.use_cases import (
    GetAvailableLibrariesUseCase,
    RenderChartFamilyUseCase,
)
from chart_factory.domain.entities import ChartRenderResult, SalesDataset
from chart_factory.infrastructure.factories import CHART_FACTORIES

# ── Page configuration ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Chart Visualization Factory",
    page_icon="📊",
    layout="wide",
)

# ── Sidebar — factory selector ─────────────────────────────────────────────────

st.sidebar.title("Abstract Factory")
st.sidebar.markdown(
    "Select a chart library. The **same data** is rendered by three different "
    "concrete families (Plotly, Matplotlib, Altair) without changing the client code."
)

library_use_case = GetAvailableLibrariesUseCase(factories=CHART_FACTORIES)
library_options = library_use_case.execute()

selected_library: str = st.sidebar.selectbox(
    "Chart Library (ConcreteFactory)",
    options=library_options,
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Pattern roles:**")
st.sidebar.markdown(
    "- `ChartFactory` → AbstractFactory  \n"
    "- `PlotlyChartFactory` → ConcreteFactory  \n"
    "- `LineChart / BarChart / PieChart` → AbstractProduct  \n"
    "- `PlotlyLineChart` etc. → ConcreteProduct  \n"
    "- `RenderChartFamilyUseCase` → Client  \n"
)

# ── Main area ──────────────────────────────────────────────────────────────────

st.title("Chart Visualization Factory")
st.markdown(
    f"Rendering charts using **{selected_library}** — swap the factory in the "
    "sidebar to see the same data rendered by a different library family."
)

# Build dataset and execute use case
dataset = SalesDataset.build_synthetic()
factory = library_use_case.get_factory(selected_library)
render_use_case = RenderChartFamilyUseCase(factory=factory)

with st.spinner(f"Rendering {selected_library} charts..."):
    results: list[ChartRenderResult] = render_use_case.execute(dataset)

# ── Display charts ─────────────────────────────────────────────────────────────

col1, col2 = st.columns(2)

for result in results:
    if result.chart_type in ("line", "bar"):
        target = col1 if result.chart_type == "line" else col2
        with target:
            st.subheader(result.chart_type.capitalize() + " Chart")
            if isinstance(result.figure, go.Figure):
                st.plotly_chart(result.figure, use_container_width=True)
            elif isinstance(result.figure, plt.Figure):
                st.pyplot(result.figure)
            elif isinstance(result.figure, alt.Chart):
                st.altair_chart(result.figure, use_container_width=True)
    else:
        # Pie chart spans full width below the two columns
        st.subheader("Pie Chart")
        if isinstance(result.figure, go.Figure):
            st.plotly_chart(result.figure, use_container_width=True)
        elif isinstance(result.figure, plt.Figure):
            st.pyplot(result.figure)
        elif isinstance(result.figure, alt.Chart):
            st.altair_chart(result.figure, use_container_width=True)

# ── Raw data expander ──────────────────────────────────────────────────────────

with st.expander("Show raw dataset"):
    st.dataframe(dataset.to_dataframe(), use_container_width=True)
