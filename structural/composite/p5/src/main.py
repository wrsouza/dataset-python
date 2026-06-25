"""Streamlit application: Nested Dashboard UI (Composite pattern).

Composition root: loads a dashboard definition (JSON), builds the
`DashboardComponent` tree (Composite), and translates the structured
`render()` output into actual `st.*` calls. The application layer never
imports Streamlit, and this module contains no Composite tree-walking
logic of its own beyond reading the data it is given (SRP).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import streamlit as st

from src.dashboard.application.use_cases import (
    BuildDashboardTreeFromFileUseCase,
    ComputeTreeMetricsUseCase,
    RenderDashboardUseCase,
)
from src.dashboard.domain.exceptions import DashboardComponentError

DEFINITION_PATH = Path(
    os.getenv("DASHBOARD_DEFINITION_PATH", "examples/sales_dashboard.json")
)

LEAF_RENDERERS = {
    "metric_card": lambda node: st.metric(
        node["label"], node["value"], delta=node.get("delta")
    ),
    "text_block": lambda node: (
        st.markdown(node["content"]) if node["markdown"] else st.text(node["content"])
    ),
    "chart": lambda node: st.line_chart(dict(node["series"])),
}


@st.cache_resource
def get_rendered_tree(definition_path: Path) -> dict[str, Any]:
    """Build the component tree once per session and return its render data."""
    build_use_case = BuildDashboardTreeFromFileUseCase()
    render_use_case = RenderDashboardUseCase()
    tree = build_use_case.execute(definition_path)
    return render_use_case.execute(tree)


@st.cache_resource
def get_tree_metrics(definition_path: Path) -> dict[str, int]:
    """Build the component tree once per session and return aggregate metrics."""
    build_use_case = BuildDashboardTreeFromFileUseCase()
    metrics_use_case = ComputeTreeMetricsUseCase()
    tree = build_use_case.execute(definition_path)
    metrics = metrics_use_case.execute(tree)
    return {
        "widget_count": metrics.widget_count,
        "depth": metrics.depth,
        "container_count": metrics.container_count,
    }


def render_node(node: dict[str, Any]) -> None:
    """Render one node of the structured tree using the right Streamlit call.

    The client (this function) never checks "is this a leaf or a
    container?" beyond dispatching on `type` — it simply recurses into
    `children` when present, which is exactly the transparency the
    Composite pattern provides.
    """
    node_type = node["type"]
    leaf_renderer = LEAF_RENDERERS.get(node_type)
    if leaf_renderer is not None:
        leaf_renderer(node)
        return

    children = node.get("children", [])
    if node_type == "row":
        columns = st.columns(len(children)) if children else []
        for column, child in zip(columns, children, strict=True):
            with column:
                render_node(child)
    elif node_type == "tab_group":
        labels = node.get("tab_labels", [child["name"] for child in children])
        tabs = st.tabs(labels) if children else []
        for tab, child in zip(tabs, children, strict=True):
            with tab:
                render_node(child)
    else:
        for child in children:
            render_node(child)


def main() -> None:
    """Streamlit entry point."""
    st.set_page_config(page_title="Nested Dashboard UI", layout="wide")
    st.title("Nested Dashboard UI — Composite Pattern")
    st.caption(
        "Widgets atômicos (metric_card, text_block, chart) e containers "
        "de layout (row, column, tab_group) compartilham a mesma interface "
        "DashboardComponent — o código de renderização trata ambos de "
        "forma transparente."
    )

    try:
        rendered_tree = get_rendered_tree(DEFINITION_PATH)
        metrics = get_tree_metrics(DEFINITION_PATH)
    except DashboardComponentError as exc:
        st.error(f"Erro ao montar o dashboard: {exc}")
        return

    with st.sidebar:
        st.subheader("Métricas da árvore")
        st.metric("Widgets", metrics["widget_count"])
        st.metric("Containers", metrics["container_count"])
        st.metric("Profundidade", metrics["depth"])

    render_node(rendered_tree)


if __name__ == "__main__":
    main()
