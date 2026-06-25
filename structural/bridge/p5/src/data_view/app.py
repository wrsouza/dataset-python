"""Streamlit application: Data Source Bridge.

Composition root: builds concrete DataSource implementations (SQL Server,
MongoDB) and injects them into SummarizedDataView (the Abstraction), which
depends only on the DataSource interface (DIP). The UI never imports
pyodbc or pymongo directly.
"""

from __future__ import annotations

import os

import streamlit as st

from data_view.application.use_cases import (
    DataView,
    ListAvailableSourcesUseCase,
    LoadReportUseCase,
)
from data_view.domain.entities import ConnectionConfig, QueryResult
from data_view.infrastructure.factory import build_default_views


def _sqlserver_config() -> ConnectionConfig:
    """Read SQL Server connection settings from the environment."""
    return ConnectionConfig(
        host=os.getenv("SQLSERVER_HOST", "localhost"),
        port=int(os.getenv("SQLSERVER_PORT", "1433")),
        database=os.getenv("SQLSERVER_DATABASE", "reports"),
        username=os.getenv("SQLSERVER_USER", "sa"),
        password=os.getenv("SQLSERVER_PASSWORD", ""),
    )


def _mongodb_config() -> ConnectionConfig:
    """Read MongoDB connection settings from the environment."""
    return ConnectionConfig(
        host=os.getenv("MONGODB_HOST", "localhost"),
        port=int(os.getenv("MONGODB_PORT", "27017")),
        database=os.getenv("MONGODB_DATABASE", "reports"),
        username=os.getenv("MONGODB_USER", ""),
        password=os.getenv("MONGODB_PASSWORD", ""),
        extra={"uri": os.getenv("MONGODB_URI", "")},
    )


@st.cache_resource
def get_views() -> dict[str, DataView]:
    """Build (once per session) the registry of available data views."""
    return dict(build_default_views(_sqlserver_config(), _mongodb_config()))


def render_result(result: QueryResult, summary: str) -> None:
    """Render a QueryResult as a Streamlit table plus a summary caption."""
    st.caption(summary)
    if result.is_empty():
        st.info("Nenhum registro encontrado.")
        return
    st.dataframe(result.to_rows(), use_container_width=True)


def main() -> None:
    """Streamlit entry point."""
    st.set_page_config(page_title="Data Source Bridge", layout="wide")
    st.title("Data Source Bridge — Bridge Pattern")
    st.caption(
        "A mesma abstração de consulta (DataView) funciona com SQL Server ou "
        "MongoDB sem alterar uma linha da camada de aplicação — apenas troca "
        "o DataSource (Implementor) injetado."
    )

    views = get_views()
    list_use_case = ListAvailableSourcesUseCase(views)
    source_names = list_use_case.execute()

    selected_name = st.selectbox("Fonte de dados", options=source_names)
    collection = st.text_input("Tabela / Coleção", value="customers")
    run_query = st.button("Consultar")

    if not run_query:
        st.info("Configure a fonte e clique em 'Consultar'.")
        return

    selected_view = views[selected_name]
    load_use_case = LoadReportUseCase(selected_view)
    try:
        result = load_use_case.execute(collection, filters={})
    except Exception as exc:  # noqa: BLE001 - surfaced to the end user
        st.error(f"Falha ao consultar '{selected_name}': {exc}")
        return

    summary = f"{len(result.records)} registro(s) de '{collection}' via {selected_name}"
    render_result(result, summary)


if __name__ == "__main__":
    main()
