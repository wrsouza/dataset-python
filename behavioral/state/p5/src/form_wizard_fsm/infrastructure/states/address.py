"""AddressStep — second step; collects shipping address."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from form_wizard_fsm.domain.interfaces import WizardStep

if TYPE_CHECKING:
    from form_wizard_fsm.domain.entities import WizardSession


class AddressStep(WizardStep):
    """Collects the user's shipping address."""

    def next_step(self, ctx: WizardSession, data: dict[str, Any]) -> None:
        from form_wizard_fsm.infrastructure.states.review import (  # noqa: PLC0415
            ReviewStep,
        )

        ctx.data.update(data)
        ctx.transition_to(ReviewStep(), "next_step")

    def previous_step(self, ctx: WizardSession) -> None:
        from form_wizard_fsm.infrastructure.states.personal_info import (  # noqa: PLC0415
            PersonalInfoStep,
        )

        ctx.transition_to(PersonalInfoStep(), "previous_step")

    def get_name(self) -> str:
        return "Address"

    def get_allowed_transitions(self) -> list[str]:
        return ["next_step", "previous_step"]
