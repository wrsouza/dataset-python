"""Integration-style test exercising the full wizard flow, mirroring how
the Streamlit app wires the use cases and steps together."""

from __future__ import annotations

from form_wizard_fsm.application.use_cases import (
    AdvanceWizardUseCase,
    GoBackUseCase,
    SubmitWizardUseCase,
)
from form_wizard_fsm.domain.entities import WizardSession


def test_full_wizard_flow_with_a_back_step() -> None:
    session = WizardSession(session_id="s1")
    advance = AdvanceWizardUseCase()
    go_back = GoBackUseCase()

    advance.execute(session, {"name": "Ana", "email": "ana@example.com"})
    assert session.get_current_step_name() == "Address"

    advance.execute(session, {"street": "Main St", "city": "Springfield"})
    assert session.get_current_step_name() == "Review"

    go_back.execute(session)
    assert session.get_current_step_name() == "Address"

    advance.execute(session, {"street": "Other St", "city": "Springfield"})
    assert session.get_current_step_name() == "Review"
    assert session.data["street"] == "Other St"

    SubmitWizardUseCase().execute(session)
    assert session.get_current_step_name() == "Submitted"
    assert session.data == {
        "name": "Ana",
        "email": "ana@example.com",
        "street": "Other St",
        "city": "Springfield",
    }
