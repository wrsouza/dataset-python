"""Streamlit application: Analysis Session Snapshots.

Composition root: builds the MongoDB-backed caretaker and a fixed
session id for the current Streamlit session (`st.session_state`),
then hands it to the use cases. Every "Run analysis" click creates a
new snapshot; "Undo" discards the latest one and restores the
previous parameters/results.
"""

from __future__ import annotations

import uuid

import streamlit as st

from analysis_session_memento.application.use_cases import (
    GetAnalysisHistoryUseCase,
    GetAnalysisStateUseCase,
    SaveAnalysisInput,
    SaveAnalysisUseCase,
    UndoAnalysisUseCase,
)
from analysis_session_memento.domain.entities import NoHistoryError
from analysis_session_memento.infrastructure.caretaker import MongoAnalysisCaretaker
from analysis_session_memento.infrastructure.factory import build_snapshots_collection


def get_session_id() -> str:
    if "analysis_session_id" not in st.session_state:
        st.session_state["analysis_session_id"] = str(uuid.uuid4())
    return str(st.session_state["analysis_session_id"])


def get_caretaker() -> MongoAnalysisCaretaker:
    if "caretaker" not in st.session_state:
        st.session_state["caretaker"] = MongoAnalysisCaretaker(
            build_snapshots_collection()
        )
    caretaker: MongoAnalysisCaretaker = st.session_state["caretaker"]
    return caretaker


def run_analysis(dataset_filter: str, threshold: float) -> dict[str, float]:
    """Stand-in analysis: a deterministic, cheap calculation over the
    chosen parameters — the focus of this project is the Memento
    pattern, not the analysis itself."""
    matches = len(dataset_filter) * 7
    return {"matches": float(matches), "threshold_squared": threshold**2}


def main() -> None:
    st.set_page_config(page_title="Analysis Session Snapshots", layout="wide")
    st.title("Analysis Session Snapshots — Memento Pattern")
    st.caption(
        "Cada execução cria um snapshot imutável dos parâmetros e resultados. "
        "'Desfazer' descarta o snapshot mais recente e restaura o anterior."
    )

    session_id = get_session_id()
    caretaker = get_caretaker()

    dataset_filter = st.text_input("Filtro do dataset", value="orders")
    threshold = st.slider("Threshold", min_value=0.0, max_value=10.0, value=5.0)
    label = st.text_input("Rótulo do snapshot", value="manual")

    if st.button("Executar análise"):
        results = run_analysis(dataset_filter, threshold)
        save = SaveAnalysisUseCase(caretaker)
        save.execute(
            SaveAnalysisInput(
                session_id=session_id,
                parameters={"dataset_filter": dataset_filter, "threshold": threshold},
                results=results,
                label=label,
            )
        )

    if st.button("Desfazer"):
        try:
            UndoAnalysisUseCase(caretaker).execute(session_id)
        except NoHistoryError:
            st.warning("Nenhum histórico disponível para desfazer.")

    try:
        current = GetAnalysisStateUseCase(caretaker).execute(session_id)
    except NoHistoryError:
        st.info("Nenhuma análise executada ainda.")
        return

    st.subheader(f"Estado atual (v{current.version}, '{current.label}')")
    st.json({"parameters": current.parameters, "results": current.results})

    st.subheader("Histórico")
    history = GetAnalysisHistoryUseCase(caretaker).execute(session_id)
    st.table([{"version": s.version, "label": s.label, **s.results} for s in history])


if __name__ == "__main__":
    main()
