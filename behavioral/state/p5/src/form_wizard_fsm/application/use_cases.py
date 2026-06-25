"""Application use cases for the Multi-step Form Wizard.

Thin wrappers around WizardSession — kept separate from the Streamlit
app so the FSM logic can be tested and reused without ever importing
`streamlit`.
"""

from __future__ import annotations

from typing import Any

from form_wizard_fsm.domain.entities import WizardSession


class AdvanceWizardUseCase:
    def execute(self, session: WizardSession, data: dict[str, Any]) -> WizardSession:
        session.next_step(data)
        return session


class GoBackUseCase:
    def execute(self, session: WizardSession) -> WizardSession:
        session.previous_step()
        return session


class SubmitWizardUseCase:
    def execute(self, session: WizardSession) -> WizardSession:
        session.submit()
        return session
