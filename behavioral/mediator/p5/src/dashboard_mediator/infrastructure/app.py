"""Streamlit application: Dashboard Component Mediator.

Composition root: builds (or reuses) the InMemoryDashboardMediator in
`st.session_state` so it survives Streamlit reruns, and hands it to the
use cases. The three widgets below (filter panel, table, summary) never
reference one another — each only talks to the mediator.
"""

from __future__ import annotations

import streamlit as st

from dashboard_mediator.application.use_cases import (
    GetDashboardDataUseCase,
    UpdateFilterUseCase,
)
from dashboard_mediator.domain.interfaces import DashboardMediator
from dashboard_mediator.infrastructure.in_memory_mediator import (
    InMemoryDashboardMediator,
)
from dashboard_mediator.infrastructure.sample_data import SAMPLE_PRODUCTS


def get_mediator() -> DashboardMediator:
    """Build (or reuse) the mediator for this Streamlit session."""
    if "mediator" not in st.session_state:
        st.session_state["mediator"] = InMemoryDashboardMediator(SAMPLE_PRODUCTS)
    mediator: DashboardMediator = st.session_state["mediator"]
    return mediator


def render_filter_panel(mediator: DashboardMediator) -> None:
    """Widget: lets the user change the shared filter."""
    st.subheader("Filtros")
    use_case = GetDashboardDataUseCase(mediator)
    data = use_case.execute()

    category_options = ["(todas)", *data.categories]
    selected = st.selectbox("Categoria", options=category_options)
    max_price = st.slider("Preço máximo", min_value=0.0, max_value=1500.0, value=1500.0)

    UpdateFilterUseCase(mediator).execute(
        category=None if selected == "(todas)" else selected,
        max_price=max_price,
    )


def render_table_widget(mediator: DashboardMediator) -> None:
    """Widget: shows the currently filtered products as a table."""
    st.subheader("Produtos filtrados")
    data = GetDashboardDataUseCase(mediator).execute()
    if not data.products:
        st.info("Nenhum produto corresponde ao filtro atual.")
        return
    st.table(
        [
            {"name": p.name, "category": p.category, "price": p.price}
            for p in data.products
        ]
    )


def render_summary_widget(mediator: DashboardMediator) -> None:
    """Widget: shows aggregate counts derived from the same filtered dataset."""
    st.subheader("Resumo")
    data = GetDashboardDataUseCase(mediator).execute()
    col1, col2 = st.columns(2)
    col1.metric("Produtos no filtro", len(data.products))
    total = sum(p.price for p in data.products)
    col2.metric("Valor total", f"${total:.2f}")


def main() -> None:
    """Streamlit entry point."""
    st.set_page_config(page_title="Dashboard Component Mediator", layout="wide")
    st.title("Dashboard Component Mediator — Mediator Pattern")
    st.caption(
        "Os três widgets abaixo (filtro, tabela, resumo) nunca se referenciam "
        "diretamente — todos leem e escrevem através do mesmo "
        "InMemoryDashboardMediator."
    )

    mediator = get_mediator()

    render_filter_panel(mediator)
    st.divider()
    left, right = st.columns(2)
    with left:
        render_table_widget(mediator)
    with right:
        render_summary_widget(mediator)


if __name__ == "__main__":
    main()
