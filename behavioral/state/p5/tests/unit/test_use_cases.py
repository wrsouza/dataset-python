"""Unit tests for the Multi-step Form Wizard use cases."""

from __future__ import annotations

from form_wizard_fsm.application.use_cases import (
    AdvanceWizardUseCase,
    GoBackUseCase,
    SubmitWizardUseCase,
)
from form_wizard_fsm.domain.entities import WizardSession


def test_advance_wizard_use_case_merges_data_and_advances() -> None:
    session = WizardSession(session_id="s1")

    AdvanceWizardUseCase().execute(session, {"name": "Ana"})

    assert session.get_current_step_name() == "Address"
    assert session.data == {"name": "Ana"}


def test_go_back_use_case_returns_to_previous_step() -> None:
    session = WizardSession(session_id="s1")
    AdvanceWizardUseCase().execute(session, {"name": "Ana"})

    GoBackUseCase().execute(session)

    assert session.get_current_step_name() == "PersonalInfo"


def test_submit_wizard_use_case_transitions_to_submitted() -> None:
    session = WizardSession(session_id="s1")
    AdvanceWizardUseCase().execute(session, {})
    AdvanceWizardUseCase().execute(session, {})

    SubmitWizardUseCase().execute(session)

    assert session.get_current_step_name() == "Submitted"
