"""Streamlit application: Live Dashboard.

Composition root: builds the Pub/Sub-backed publisher and the local
DashboardStateObserver once per Streamlit session (`st.session_state`),
then hands them to the use cases. Every "Publish metric" click fans out
to the dashboard's own state AND to the GCP Pub/Sub topic.
"""

from __future__ import annotations

import random

import streamlit as st

from live_dashboard_observer.application.use_cases import (
    GetDashboardStateUseCase,
    PublishMetricUseCase,
)
from live_dashboard_observer.domain.interfaces import MetricsPublisher
from live_dashboard_observer.infrastructure.factory import build_publisher
from live_dashboard_observer.infrastructure.observers import DashboardStateObserver

METRIC_NAMES = ["cpu_usage", "active_users", "error_rate"]


def get_publisher() -> MetricsPublisher:
    if "publisher" not in st.session_state:
        new_publisher = build_publisher()
        state_observer = DashboardStateObserver()
        new_publisher.subscribe(state_observer)
        st.session_state["publisher"] = new_publisher
        st.session_state["state_observer"] = state_observer
    publisher: MetricsPublisher = st.session_state["publisher"]
    return publisher


def get_state_observer() -> DashboardStateObserver:
    get_publisher()  # ensures both are initialised together
    observer: DashboardStateObserver = st.session_state["state_observer"]
    return observer


def main() -> None:
    st.set_page_config(page_title="Live Dashboard", layout="wide")
    st.title("Live Dashboard — Observer Pattern")
    st.caption(
        "Cada métrica publicada notifica o estado do dashboard (observador local) "
        "e é publicada no tópico GCP Pub/Sub (observadores remotos)."
    )

    publisher = get_publisher()
    state_observer = get_state_observer()

    metric_name = st.selectbox("Métrica", options=METRIC_NAMES)
    if st.button("Simular atualização"):
        value = round(random.uniform(0, 100), 2)
        PublishMetricUseCase(publisher).execute(metric_name, value)

    st.subheader("Estado atual do dashboard")
    state = GetDashboardStateUseCase(state_observer).execute()
    if not state:
        st.info("Nenhuma métrica publicada ainda.")
        return

    st.table(
        [
            {
                "metric": event.metric_name,
                "value": event.value,
                "occurred_at": event.occurred_at.isoformat(),
            }
            for event in state.values()
        ]
    )


if __name__ == "__main__":
    main()
