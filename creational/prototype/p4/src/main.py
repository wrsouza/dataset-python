"""Streamlit application: Dashboard Config Cloner (Prototype pattern).

Composition root: builds the JsonDashboardRegistry (concrete infrastructure)
and injects it into the use cases (application layer), which depend only
on the DashboardRegistry abstraction (DIP).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import streamlit as st

from dashboard.application.use_cases import (
    CloneDashboardUseCase,
    EditClonedDashboardUseCase,
    GetDashboardTemplateUseCase,
    ListDashboardTemplatesUseCase,
)
from dashboard.domain.interfaces import DashboardConfig
from dashboard.infrastructure.registry import (
    JsonDashboardRegistry,
    build_default_registry,
)

REGISTRY_PATH = Path(os.getenv("REGISTRY_PATH", "data/registry.json"))


@st.cache_resource
def get_registry() -> JsonDashboardRegistry:
    """Build (or load) the prototype registry once per Streamlit session."""
    return build_default_registry(REGISTRY_PATH)


def render_config(config: DashboardConfig, heading: str) -> None:
    """Render a dashboard config as a read-only summary panel."""
    st.subheader(heading)
    st.json(config.to_dict())


def render_editor(config: DashboardConfig) -> dict[str, Any]:
    """Render input widgets to edit a cloned config; return the overrides."""
    data = config.to_dict()
    title = st.text_input("Título", value=data["title"])
    date_range = st.text_input("Período", value=data["date_range"])
    chart_type = st.text_input("Tipo de gráfico", value=data["chart_type"])
    theme = st.selectbox(
        "Tema", options=["light", "dark"], index=0 if data["theme"] == "light" else 1
    )
    metrics_raw = st.text_area(
        "Métricas (uma por linha)", value="\n".join(data["metrics"])
    )
    metrics = [line.strip() for line in metrics_raw.splitlines() if line.strip()]
    return {
        "title": title,
        "date_range": date_range,
        "chart_type": chart_type,
        "theme": theme,
        "metrics": metrics,
    }


def main() -> None:
    """Streamlit entry point."""
    st.set_page_config(page_title="Dashboard Config Cloner", layout="wide")
    st.title("Dashboard Config Cloner — Prototype Pattern")
    st.caption(
        "Clone configurações de dashboard pré-definidas e edite a cópia sem "
        "afetar o template original (cópia profunda / deepcopy)."
    )

    registry = get_registry()
    list_use_case = ListDashboardTemplatesUseCase(registry)
    get_use_case = GetDashboardTemplateUseCase(registry)
    clone_use_case = CloneDashboardUseCase(registry)
    edit_use_case = EditClonedDashboardUseCase()

    template_names = list_use_case.execute()
    if not template_names:
        st.warning("Nenhum template registrado.")
        return

    selected = st.selectbox("Escolha um prototype", options=template_names)
    original = get_use_case.execute(selected)

    col_left, col_right = st.columns(2)
    with col_left:
        render_config(original, "Original (template no registry)")

    st.divider()
    st.subheader("Clonar e editar")

    if st.button("Clonar prototype"):
        cloned = clone_use_case.execute(selected, overrides={})
        st.session_state["cloned_config"] = cloned

    cloned_config = st.session_state.get("cloned_config")
    if cloned_config is not None:
        overrides = render_editor(cloned_config)
        edited = edit_use_case.execute(cloned_config, overrides)
        with col_right:
            render_config(edited, "Cópia editada (independente do original)")

        st.success(
            "A cópia foi alterada e o template original permanece intacto — "
            "prova de que clone() faz deep copy, não shallow copy."
        )
    else:
        st.info("Clique em 'Clonar prototype' para criar uma cópia editável.")


if __name__ == "__main__":
    main()
