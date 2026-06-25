"""Integration-style test exercising the full save -> undo -> history flow
against a mongomock-backed caretaker, mirroring how the Streamlit app
wires the use cases together."""

from __future__ import annotations

from analysis_session_memento.application.use_cases import (
    GetAnalysisHistoryUseCase,
    GetAnalysisStateUseCase,
    SaveAnalysisInput,
    SaveAnalysisUseCase,
    UndoAnalysisUseCase,
)
from analysis_session_memento.infrastructure.app import run_analysis
from analysis_session_memento.infrastructure.caretaker import MongoAnalysisCaretaker


def test_run_analysis_is_deterministic() -> None:
    first = run_analysis("orders", 5.0)
    second = run_analysis("orders", 5.0)

    assert first == second
    assert first["matches"] == len("orders") * 7
    assert first["threshold_squared"] == 25.0


def test_full_save_undo_history_workflow(caretaker: MongoAnalysisCaretaker) -> None:
    save = SaveAnalysisUseCase(caretaker)
    save.execute(
        SaveAnalysisInput(
            session_id="session-1",
            parameters={"dataset_filter": "orders", "threshold": 5.0},
            results=run_analysis("orders", 5.0),
            label="manual",
        )
    )
    save.execute(
        SaveAnalysisInput(
            session_id="session-1",
            parameters={"dataset_filter": "customers", "threshold": 2.0},
            results=run_analysis("customers", 2.0),
            label="manual",
        )
    )

    current = GetAnalysisStateUseCase(caretaker).execute("session-1")
    assert current.parameters["dataset_filter"] == "customers"

    restored = UndoAnalysisUseCase(caretaker).execute("session-1")
    assert restored.parameters["dataset_filter"] == "orders"

    history = GetAnalysisHistoryUseCase(caretaker).execute("session-1")
    assert len(history) == 1
