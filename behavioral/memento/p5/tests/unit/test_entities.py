"""Unit tests for AnalysisSession and AnalysisSnapshot domain entities."""

from __future__ import annotations

import pytest

from analysis_session_memento.domain.entities import AnalysisSession, AnalysisSnapshot


def test_snapshot_rejects_invalid_version() -> None:
    with pytest.raises(ValueError, match="version"):
        AnalysisSnapshot(parameters={}, results={}, version=0, label="x")


def test_snapshot_rejects_empty_label() -> None:
    with pytest.raises(ValueError, match="label"):
        AnalysisSnapshot(parameters={}, results={}, version=1, label="   ")


def test_create_snapshot_captures_current_state() -> None:
    session = AnalysisSession(
        session_id="s1",
        parameters={"threshold": 5},
        results={"matches": 10},
        current_version=1,
    )
    session.set_label("manual")

    snapshot = session.create_snapshot()

    assert snapshot.parameters == {"threshold": 5}
    assert snapshot.results == {"matches": 10}
    assert snapshot.label == "manual"


def test_restore_replaces_state_and_version() -> None:
    session = AnalysisSession(session_id="s1", parameters={}, results={})
    snapshot = AnalysisSnapshot(
        parameters={"threshold": 9}, results={"matches": 1}, version=5, label="x"
    )

    session.restore(snapshot)

    assert session.parameters == {"threshold": 9}
    assert session.results == {"matches": 1}
    assert session.current_version == 5


def test_update_replaces_state_and_advances_version() -> None:
    session = AnalysisSession(session_id="s1", parameters={}, results={})

    session.update({"threshold": 1}, {"matches": 7})

    assert session.parameters == {"threshold": 1}
    assert session.results == {"matches": 7}
    assert session.current_version == 1
