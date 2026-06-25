"""Domain interfaces for the Multi-step Form Wizard.

Defines the State ABC following the State pattern.
OCP: adding a new step requires only a new class, no modification of
existing code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from form_wizard_fsm.domain.entities import WizardSession


class InvalidTransitionError(Exception):
    """Raised when an invalid step transition is attempted."""

    def __init__(self, from_step: str, action: str) -> None:
        self.from_step = from_step
        self.action = action
        super().__init__(f"Cannot perform '{action}' on wizard step '{from_step}'.")


class WizardStep(ABC):
    """Abstract base for all wizard steps.

    Each concrete step implements only the transitions it allows;
    invalid transitions raise InvalidTransitionError by default.
    """

    def next_step(self, ctx: WizardSession, data: dict[str, Any]) -> None:
        raise InvalidTransitionError(self.get_name(), "next_step")

    def previous_step(self, ctx: WizardSession) -> None:
        raise InvalidTransitionError(self.get_name(), "previous_step")

    def submit(self, ctx: WizardSession) -> None:
        raise InvalidTransitionError(self.get_name(), "submit")

    @abstractmethod
    def get_name(self) -> str:
        """Return the canonical name of this step."""

    @abstractmethod
    def get_allowed_transitions(self) -> list[str]:
        """Return the list of allowed action names from this step."""
