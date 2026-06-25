"""SubmittedStep — terminal step; the form has been fully submitted."""

from __future__ import annotations

from form_wizard_fsm.domain.interfaces import WizardStep


class SubmittedStep(WizardStep):
    """Form was submitted; no further transitions are allowed."""

    def get_name(self) -> str:
        return "Submitted"

    def get_allowed_transitions(self) -> list[str]:
        return []
