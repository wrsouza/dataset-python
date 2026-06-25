"""PersonalInfoStep — first step; collects name and email."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from form_wizard_fsm.domain.interfaces import WizardStep

if TYPE_CHECKING:
    from form_wizard_fsm.domain.entities import WizardSession


class PersonalInfoStep(WizardStep):
    """Collects the user's name and email."""

    def next_step(self, ctx: WizardSession, data: dict[str, Any]) -> None:
        from form_wizard_fsm.infrastructure.states.address import (  # noqa: PLC0415
            AddressStep,
        )

        ctx.data.update(data)
        ctx.transition_to(AddressStep(), "next_step")

    def get_name(self) -> str:
        return "PersonalInfo"

    def get_allowed_transitions(self) -> list[str]:
        return ["next_step"]
