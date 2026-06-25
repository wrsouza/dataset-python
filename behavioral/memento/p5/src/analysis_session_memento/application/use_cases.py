"""Application use cases for Analysis Session Snapshots.

Each use case has a single responsibility and depends only on the
AnalysisCaretaker abstraction (DIP). The AnalysisSession Originator is
reconstructed on demand from the latest snapshot — MongoDB is the
single source of truth, so there is no separate session repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from analysis_session_memento.domain.entities import (
    AnalysisSession,
    AnalysisSnapshot,
    NoHistoryError,
)
from analysis_session_memento.domain.interfaces import AnalysisCaretaker


@dataclass
class SaveAnalysisInput:
    session_id: str
    parameters: dict[str, Any]
    results: dict[str, Any]
    label: str = "autosave"


class SaveAnalysisUseCase:
    """Records a new analysis run and snapshots the result.

    SRP: only handles the save flow.
    DIP: depends on the AnalysisCaretaker abstraction, not a concrete backend.
    """

    def __init__(self, caretaker: AnalysisCaretaker) -> None:
        self._caretaker = caretaker

    def execute(self, data: SaveAnalysisInput) -> AnalysisSnapshot:
        try:
            previous = self._caretaker.latest(data.session_id)
            session = AnalysisSession(
                session_id=data.session_id,
                parameters=dict(previous.parameters),
                results=dict(previous.results),
                current_version=previous.version,
            )
        except NoHistoryError:  # first save for this session
            session = AnalysisSession(
                session_id=data.session_id, parameters={}, results={}
            )

        session.set_label(data.label)
        session.update(data.parameters, data.results)
        snapshot = session.create_snapshot()
        self._caretaker.save(data.session_id, snapshot)
        return snapshot


class UndoAnalysisUseCase:
    """Reverts an analysis session to its previous snapshot."""

    def __init__(self, caretaker: AnalysisCaretaker) -> None:
        self._caretaker = caretaker

    def execute(self, session_id: str) -> AnalysisSnapshot:
        return self._caretaker.undo(session_id)


class GetAnalysisStateUseCase:
    """Returns the current (latest) state of an analysis session."""

    def __init__(self, caretaker: AnalysisCaretaker) -> None:
        self._caretaker = caretaker

    def execute(self, session_id: str) -> AnalysisSnapshot:
        return self._caretaker.latest(session_id)


class GetAnalysisHistoryUseCase:
    """Returns the full snapshot history of an analysis session."""

    def __init__(self, caretaker: AnalysisCaretaker) -> None:
        self._caretaker = caretaker

    def execute(self, session_id: str) -> list[AnalysisSnapshot]:
        return self._caretaker.history(session_id)
