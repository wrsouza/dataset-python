"""Unit tests for Analysis Session Snapshots use cases."""

from __future__ import annotations

import pytest

from analysis_session_memento.application.use_cases import (
    GetAnalysisHistoryUseCase,
    GetAnalysisStateUseCase,
    SaveAnalysisInput,
    SaveAnalysisUseCase,
    UndoAnalysisUseCase,
)
from analysis_session_memento.domain.entities import NoHistoryError
from analysis_session_memento.infrastructure.caretaker import MongoAnalysisCaretaker


def test_save_analysis_creates_first_snapshot(
    caretaker: MongoAnalysisCaretaker,
) -> None:
    use_case = SaveAnalysisUseCase(caretaker)

    snapshot = use_case.execute(
        SaveAnalysisInput(
            session_id="session-1",
            parameters={"threshold": 5},
            results={"matches": 10},
        )
    )

    assert snapshot.parameters == {"threshold": 5}
    assert snapshot.version == 1


def test_save_analysis_advances_version_on_second_call(
    caretaker: MongoAnalysisCaretaker,
) -> None:
    use_case = SaveAnalysisUseCase(caretaker)
    use_case.execute(
        SaveAnalysisInput(session_id="session-1", parameters={"a": 1}, results={})
    )

    snapshot = use_case.execute(
        SaveAnalysisInput(session_id="session-1", parameters={"a": 2}, results={})
    )

    assert snapshot.version == 2
    assert snapshot.parameters == {"a": 2}


def test_undo_analysis_reverts_to_previous_snapshot(
    caretaker: MongoAnalysisCaretaker,
) -> None:
    save = SaveAnalysisUseCase(caretaker)
    save.execute(
        SaveAnalysisInput(session_id="session-1", parameters={"a": 1}, results={})
    )
    save.execute(
        SaveAnalysisInput(session_id="session-1", parameters={"a": 2}, results={})
    )

    undo = UndoAnalysisUseCase(caretaker)
    restored = undo.execute("session-1")

    assert restored.version == 1
    assert restored.parameters == {"a": 1}


def test_undo_analysis_raises_without_history(
    caretaker: MongoAnalysisCaretaker,
) -> None:
    undo = UndoAnalysisUseCase(caretaker)

    with pytest.raises(NoHistoryError):
        undo.execute("unknown-session")


def test_get_analysis_state_returns_latest_snapshot(
    caretaker: MongoAnalysisCaretaker,
) -> None:
    save = SaveAnalysisUseCase(caretaker)
    save.execute(
        SaveAnalysisInput(session_id="session-1", parameters={"a": 1}, results={})
    )

    get_state = GetAnalysisStateUseCase(caretaker)
    snapshot = get_state.execute("session-1")

    assert snapshot.parameters == {"a": 1}


def test_get_analysis_history_returns_all_snapshots(
    caretaker: MongoAnalysisCaretaker,
) -> None:
    save = SaveAnalysisUseCase(caretaker)
    save.execute(
        SaveAnalysisInput(session_id="session-1", parameters={"a": 1}, results={})
    )
    save.execute(
        SaveAnalysisInput(session_id="session-1", parameters={"a": 2}, results={})
    )

    get_history = GetAnalysisHistoryUseCase(caretaker)
    history = get_history.execute("session-1")

    assert [snap.version for snap in history] == [1, 2]
