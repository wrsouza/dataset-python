"""Unit tests for MongoAnalysisCaretaker, using mongomock."""

from __future__ import annotations

import pytest

from analysis_session_memento.domain.entities import AnalysisSnapshot, NoHistoryError
from analysis_session_memento.infrastructure.caretaker import MongoAnalysisCaretaker


def test_save_and_latest_roundtrip(caretaker: MongoAnalysisCaretaker) -> None:
    snapshot = AnalysisSnapshot(
        parameters={"threshold": 5}, results={"matches": 10}, version=1, label="manual"
    )
    caretaker.save("session-1", snapshot)

    latest = caretaker.latest("session-1")

    assert latest.parameters == {"threshold": 5}
    assert latest.results == {"matches": 10}
    assert latest.version == 1


def test_latest_raises_when_no_history(caretaker: MongoAnalysisCaretaker) -> None:
    with pytest.raises(NoHistoryError):
        caretaker.latest("unknown-session")


def test_undo_returns_previous_snapshot(caretaker: MongoAnalysisCaretaker) -> None:
    caretaker.save(
        "session-1",
        AnalysisSnapshot(parameters={"v": 1}, results={}, version=1, label="s1"),
    )
    caretaker.save(
        "session-1",
        AnalysisSnapshot(parameters={"v": 2}, results={}, version=2, label="s2"),
    )

    restored = caretaker.undo("session-1")

    assert restored.version == 1
    assert restored.parameters == {"v": 1}


def test_undo_raises_when_only_one_snapshot(caretaker: MongoAnalysisCaretaker) -> None:
    caretaker.save(
        "session-1", AnalysisSnapshot(parameters={}, results={}, version=1, label="s1")
    )

    with pytest.raises(NoHistoryError):
        caretaker.undo("session-1")


def test_history_returns_all_snapshots_in_order(
    caretaker: MongoAnalysisCaretaker,
) -> None:
    caretaker.save(
        "session-1", AnalysisSnapshot(parameters={}, results={}, version=1, label="s1")
    )
    caretaker.save(
        "session-1", AnalysisSnapshot(parameters={}, results={}, version=2, label="s2")
    )
    caretaker.save(
        "session-1", AnalysisSnapshot(parameters={}, results={}, version=3, label="s3")
    )

    history = caretaker.history("session-1")

    assert [snap.version for snap in history] == [1, 2, 3]


def test_history_empty_for_unknown_session(caretaker: MongoAnalysisCaretaker) -> None:
    assert caretaker.history("unknown-session") == []
