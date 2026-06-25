"""Unit tests for RedisFormCaretaker."""

from __future__ import annotations

import pytest

from form_state_memento.domain.entities import FormSnapshot, NoHistoryError
from form_state_memento.infrastructure.caretaker import RedisFormCaretaker


def test_save_and_latest_roundtrip(caretaker: RedisFormCaretaker) -> None:
    snapshot = FormSnapshot(fields={"name": "Ana"}, step=1, label="autosave")
    caretaker.save("session-1", snapshot)

    latest = caretaker.latest("session-1")

    assert latest.fields == {"name": "Ana"}
    assert latest.step == 1
    assert latest.label == "autosave"


def test_latest_raises_when_no_history(caretaker: RedisFormCaretaker) -> None:
    with pytest.raises(NoHistoryError):
        caretaker.latest("unknown-session")


def test_undo_returns_previous_snapshot(caretaker: RedisFormCaretaker) -> None:
    caretaker.save("session-1", FormSnapshot(fields={"step": "a"}, step=1, label="s1"))
    caretaker.save("session-1", FormSnapshot(fields={"step": "b"}, step=2, label="s2"))

    restored = caretaker.undo("session-1")

    assert restored.step == 1
    assert restored.fields == {"step": "a"}


def test_undo_raises_when_only_one_snapshot(caretaker: RedisFormCaretaker) -> None:
    caretaker.save("session-1", FormSnapshot(fields={}, step=1, label="s1"))

    with pytest.raises(NoHistoryError):
        caretaker.undo("session-1")


def test_history_returns_all_snapshots_in_order(
    caretaker: RedisFormCaretaker,
) -> None:
    caretaker.save("session-1", FormSnapshot(fields={}, step=1, label="s1"))
    caretaker.save("session-1", FormSnapshot(fields={}, step=2, label="s2"))
    caretaker.save("session-1", FormSnapshot(fields={}, step=3, label="s3"))

    history = caretaker.history("session-1")

    assert [snap.step for snap in history] == [1, 2, 3]


def test_history_empty_for_unknown_session(caretaker: RedisFormCaretaker) -> None:
    assert caretaker.history("unknown-session") == []
