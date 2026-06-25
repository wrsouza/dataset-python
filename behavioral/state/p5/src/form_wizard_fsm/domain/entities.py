"""Domain entities for the Multi-step Form Wizard."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class StateTransitionRecord:
    from_state: str
    to_state: str
    action: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class WizardSession:
    """Context in the State pattern.

    Delegates all behaviour to the current _state object; accumulates
    form field values across steps in `data` so the Review step can
    show everything collected so far.
    """

    from form_wizard_fsm.domain.interfaces import WizardStep  # noqa: PLC0415

    session_id: str
    data: dict[str, Any] = field(default_factory=dict)
    history: list[StateTransitionRecord] = field(default_factory=list)
    _state: WizardStep = field(init=False)

    def __post_init__(self) -> None:
        from form_wizard_fsm.infrastructure.states.personal_info import (  # noqa: PLC0415
            PersonalInfoStep,
        )

        self._state = PersonalInfoStep()

    # ── State delegation ────────────────────────────────────────────────────────

    def next_step(self, data: dict[str, Any]) -> None:
        self._state.next_step(self, data)

    def previous_step(self) -> None:
        self._state.previous_step(self)

    def submit(self) -> None:
        self._state.submit(self)

    # ── State accessors ─────────────────────────────────────────────────────────

    def get_current_step_name(self) -> str:
        return self._state.get_name()

    def get_allowed_transitions(self) -> list[str]:
        return self._state.get_allowed_transitions()

    def transition_to(self, new_state: WizardStep, action: str) -> None:
        """Record the transition and swap the current step."""
        record = StateTransitionRecord(
            from_state=self._state.get_name(),
            to_state=new_state.get_name(),
            action=action,
        )
        self.history.append(record)
        self._state = new_state
