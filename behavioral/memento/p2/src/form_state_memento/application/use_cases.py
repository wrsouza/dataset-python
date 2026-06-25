"""Application use cases for Form State Save/Restore.

Each use case has a single responsibility and depends only on the
FormCaretaker abstraction (DIP). The FormSession Originator is
reconstructed on demand from the latest snapshot — Redis is the single
source of truth, so there is no separate session repository to keep in
sync.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from form_state_memento.domain.entities import (
    FormSession,
    FormSnapshot,
    NoHistoryError,
)
from form_state_memento.domain.interfaces import FormCaretaker


@dataclass
class SaveFormStateInput:
    session_id: str
    fields: dict[str, Any]
    step: int
    label: str = "autosave"


class SaveFormStateUseCase:
    """Applies new field values to a session and snapshots the result.

    SRP: only handles the save/autosave flow.
    DIP: depends on the FormCaretaker abstraction, not a concrete backend.
    """

    def __init__(self, caretaker: FormCaretaker) -> None:
        self._caretaker = caretaker

    def execute(self, data: SaveFormStateInput) -> FormSnapshot:
        try:
            previous = self._caretaker.latest(data.session_id)
            session = FormSession(
                session_id=data.session_id,
                fields=dict(previous.fields),
                current_step=previous.step,
            )
        except NoHistoryError:  # first save for this session
            session = FormSession(session_id=data.session_id, fields={})

        session.set_label(data.label)
        session.update_fields(data.fields, data.step)
        snapshot = session.create_snapshot()
        self._caretaker.save(data.session_id, snapshot)
        return snapshot


class UndoFormStateUseCase:
    """Reverts a form session to its previous snapshot."""

    def __init__(self, caretaker: FormCaretaker) -> None:
        self._caretaker = caretaker

    def execute(self, session_id: str) -> FormSnapshot:
        return self._caretaker.undo(session_id)


class GetFormStateUseCase:
    """Returns the current (latest) state of a form session."""

    def __init__(self, caretaker: FormCaretaker) -> None:
        self._caretaker = caretaker

    def execute(self, session_id: str) -> FormSnapshot:
        return self._caretaker.latest(session_id)


class GetFormHistoryUseCase:
    """Returns the full snapshot history of a form session."""

    def __init__(self, caretaker: FormCaretaker) -> None:
        self._caretaker = caretaker

    def execute(self, session_id: str) -> list[FormSnapshot]:
        return self._caretaker.history(session_id)
