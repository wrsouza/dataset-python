"""ReviewStep — third step; shows everything collected so far before submit."""

from __future__ import annotations

from typing import TYPE_CHECKING

from form_wizard_fsm.domain.interfaces import WizardStep

if TYPE_CHECKING:
    from form_wizard_fsm.domain.entities import WizardSession


class ReviewStep(WizardStep):
    """Lets the user review all collected data before submitting."""

    def previous_step(self, ctx: WizardSession) -> None:
        from form_wizard_fsm.infrastructure.states.address import (  # noqa: PLC0415
            AddressStep,
        )

        ctx.transition_to(AddressStep(), "previous_step")

    def submit(self, ctx: WizardSession) -> None:
        from form_wizard_fsm.infrastructure.states.submitted import (  # noqa: PLC0415
            SubmittedStep,
        )

        ctx.transition_to(SubmittedStep(), "submit")

    def get_name(self) -> str:
        return "Review"

    def get_allowed_transitions(self) -> list[str]:
        return ["previous_step", "submit"]
