"""Domain interfaces for the Workflow Approval FSM.

Defines the State ABC following the State pattern.
OCP: adding a new state requires only a new class, no modification of
existing code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from workflow_approval_fsm.domain.entities import WorkflowRequest


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, from_state: str, action: str) -> None:
        self.from_state = from_state
        self.action = action
        super().__init__(
            f"Cannot perform '{action}' on workflow request in state '{from_state}'."
        )


class WorkflowState(ABC):
    """Abstract base for all workflow request states.

    Each concrete state implements only the transitions it allows;
    invalid transitions raise InvalidTransitionError by default.
    """

    def submit(self, ctx: WorkflowRequest) -> None:
        raise InvalidTransitionError(self.get_name(), "submit")

    def approve(self, ctx: WorkflowRequest) -> None:
        raise InvalidTransitionError(self.get_name(), "approve")

    def reject(self, ctx: WorkflowRequest) -> None:
        raise InvalidTransitionError(self.get_name(), "reject")

    def request_changes(self, ctx: WorkflowRequest) -> None:
        raise InvalidTransitionError(self.get_name(), "request_changes")

    @abstractmethod
    def get_name(self) -> str:
        """Return the canonical name of this state."""

    @abstractmethod
    def get_allowed_transitions(self) -> list[str]:
        """Return the list of allowed action names from this state."""
