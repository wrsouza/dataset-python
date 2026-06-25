"""Unit tests for the WizardSession State pattern implementation."""

from __future__ import annotations

import pytest

from form_wizard_fsm.domain.entities import WizardSession
from form_wizard_fsm.domain.interfaces import InvalidTransitionError


def test_new_session_starts_at_personal_info() -> None:
    session = WizardSession(session_id="s1")

    assert session.get_current_step_name() == "PersonalInfo"
    assert session.get_allowed_transitions() == ["next_step"]


def test_next_step_from_personal_info_collects_data_and_advances() -> None:
    session = WizardSession(session_id="s1")

    session.next_step({"name": "Ana", "email": "ana@example.com"})

    assert session.get_current_step_name() == "Address"
    assert session.data == {"name": "Ana", "email": "ana@example.com"}


def test_next_step_from_address_merges_data_and_advances_to_review() -> None:
    session = WizardSession(session_id="s1")
    session.next_step({"name": "Ana"})

    session.next_step({"street": "Main St"})

    assert session.get_current_step_name() == "Review"
    assert session.data == {"name": "Ana", "street": "Main St"}


def test_previous_step_from_address_returns_to_personal_info() -> None:
    session = WizardSession(session_id="s1")
    session.next_step({"name": "Ana"})

    session.previous_step()

    assert session.get_current_step_name() == "PersonalInfo"


def test_previous_step_from_review_returns_to_address() -> None:
    session = WizardSession(session_id="s1")
    session.next_step({"name": "Ana"})
    session.next_step({"street": "Main St"})

    session.previous_step()

    assert session.get_current_step_name() == "Address"


def test_submit_from_review_transitions_to_submitted() -> None:
    session = WizardSession(session_id="s1")
    session.next_step({"name": "Ana"})
    session.next_step({"street": "Main St"})

    session.submit()

    assert session.get_current_step_name() == "Submitted"
    assert session.get_allowed_transitions() == []


def test_personal_info_rejects_previous_step() -> None:
    session = WizardSession(session_id="s1")

    with pytest.raises(InvalidTransitionError):
        session.previous_step()


def test_personal_info_rejects_submit() -> None:
    session = WizardSession(session_id="s1")

    with pytest.raises(InvalidTransitionError):
        session.submit()


def test_submitted_is_terminal() -> None:
    session = WizardSession(session_id="s1")
    session.next_step({})
    session.next_step({})
    session.submit()

    with pytest.raises(InvalidTransitionError):
        session.previous_step()


def test_history_records_each_transition() -> None:
    session = WizardSession(session_id="s1")

    session.next_step({})
    session.next_step({})
    session.previous_step()

    assert [r.action for r in session.history] == [
        "next_step",
        "next_step",
        "previous_step",
    ]
