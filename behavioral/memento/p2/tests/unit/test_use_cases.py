"""Unit tests for Form State Save/Restore use cases."""

from __future__ import annotations

import pytest

from form_state_memento.application.use_cases import (
    GetFormHistoryUseCase,
    GetFormStateUseCase,
    SaveFormStateInput,
    SaveFormStateUseCase,
    UndoFormStateUseCase,
)
from form_state_memento.domain.entities import NoHistoryError
from form_state_memento.infrastructure.caretaker import RedisFormCaretaker


def test_save_form_state_creates_first_snapshot(
    caretaker: RedisFormCaretaker,
) -> None:
    use_case = SaveFormStateUseCase(caretaker)

    snapshot = use_case.execute(
        SaveFormStateInput(
            session_id="session-1",
            fields={"email": "a@b.com"},
            step=1,
        )
    )

    assert snapshot.fields == {"email": "a@b.com"}
    assert snapshot.step == 1


def test_save_form_state_merges_with_previous_fields(
    caretaker: RedisFormCaretaker,
) -> None:
    use_case = SaveFormStateUseCase(caretaker)
    use_case.execute(
        SaveFormStateInput(session_id="session-1", fields={"name": "Ana"}, step=1)
    )

    snapshot = use_case.execute(
        SaveFormStateInput(session_id="session-1", fields={"email": "a@b.com"}, step=2)
    )

    assert snapshot.fields == {"name": "Ana", "email": "a@b.com"}
    assert snapshot.step == 2


def test_undo_form_state_reverts_to_previous_snapshot(
    caretaker: RedisFormCaretaker,
) -> None:
    save = SaveFormStateUseCase(caretaker)
    save.execute(SaveFormStateInput(session_id="session-1", fields={"a": 1}, step=1))
    save.execute(SaveFormStateInput(session_id="session-1", fields={"b": 2}, step=2))

    undo = UndoFormStateUseCase(caretaker)
    restored = undo.execute("session-1")

    assert restored.step == 1
    assert restored.fields == {"a": 1}


def test_undo_form_state_raises_without_history(
    caretaker: RedisFormCaretaker,
) -> None:
    undo = UndoFormStateUseCase(caretaker)

    with pytest.raises(NoHistoryError):
        undo.execute("unknown-session")


def test_get_form_state_returns_latest_snapshot(
    caretaker: RedisFormCaretaker,
) -> None:
    save = SaveFormStateUseCase(caretaker)
    save.execute(SaveFormStateInput(session_id="session-1", fields={"a": 1}, step=1))

    get_state = GetFormStateUseCase(caretaker)
    snapshot = get_state.execute("session-1")

    assert snapshot.fields == {"a": 1}


def test_get_form_history_returns_all_snapshots(
    caretaker: RedisFormCaretaker,
) -> None:
    save = SaveFormStateUseCase(caretaker)
    save.execute(SaveFormStateInput(session_id="session-1", fields={"a": 1}, step=1))
    save.execute(SaveFormStateInput(session_id="session-1", fields={"b": 2}, step=2))

    get_history = GetFormHistoryUseCase(caretaker)
    history = get_history.execute("session-1")

    assert [snap.step for snap in history] == [1, 2]
