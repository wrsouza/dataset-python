"""Unit tests for FormSession and FormSnapshot domain entities."""

from __future__ import annotations

import pytest

from form_state_memento.domain.entities import FormSession, FormSnapshot


def test_snapshot_rejects_invalid_step() -> None:
    with pytest.raises(ValueError, match="step"):
        FormSnapshot(fields={}, step=0, label="x")


def test_snapshot_rejects_empty_label() -> None:
    with pytest.raises(ValueError, match="label"):
        FormSnapshot(fields={}, step=1, label="   ")


def test_create_snapshot_captures_current_state() -> None:
    session = FormSession(session_id="s1", fields={"name": "Ana"}, current_step=2)
    session.set_label("manual")

    snapshot = session.create_snapshot()

    assert snapshot.fields == {"name": "Ana"}
    assert snapshot.step == 2
    assert snapshot.label == "manual"


def test_restore_replaces_fields_and_step() -> None:
    session = FormSession(session_id="s1", fields={"name": "Ana"}, current_step=1)
    snapshot = FormSnapshot(fields={"name": "Bob"}, step=5, label="x")

    session.restore(snapshot)

    assert session.fields == {"name": "Bob"}
    assert session.current_step == 5


def test_update_fields_merges_and_advances_step() -> None:
    session = FormSession(session_id="s1", fields={"name": "Ana"}, current_step=1)

    session.update_fields({"email": "a@b.com"}, new_step=2)

    assert session.fields == {"name": "Ana", "email": "a@b.com"}
    assert session.current_step == 2
