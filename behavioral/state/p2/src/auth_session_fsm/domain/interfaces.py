"""Domain interfaces for the User Auth Session FSM.

Defines the State ABC following the State pattern.
OCP: adding a new state requires only a new class, no modification of
existing code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auth_session_fsm.domain.entities import AuthSession


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, from_state: str, action: str) -> None:
        self.from_state = from_state
        self.action = action
        super().__init__(
            f"Cannot perform '{action}' on session in state '{from_state}'."
        )


class SessionState(ABC):
    """Abstract base for all auth session states.

    Each concrete state implements only the transitions it allows;
    invalid transitions raise InvalidTransitionError by default.
    """

    def login(self, ctx: AuthSession, success: bool) -> None:
        raise InvalidTransitionError(self.get_name(), "login")

    def logout(self, ctx: AuthSession) -> None:
        raise InvalidTransitionError(self.get_name(), "logout")

    def refresh(self, ctx: AuthSession) -> None:
        raise InvalidTransitionError(self.get_name(), "refresh")

    def expire(self, ctx: AuthSession) -> None:
        raise InvalidTransitionError(self.get_name(), "expire")

    def unlock(self, ctx: AuthSession) -> None:
        raise InvalidTransitionError(self.get_name(), "unlock")

    @abstractmethod
    def get_name(self) -> str:
        """Return the canonical name of this state."""

    @abstractmethod
    def get_allowed_transitions(self) -> list[str]:
        """Return the list of allowed action names from this state."""
