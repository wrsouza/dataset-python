"""Domain interfaces for the Order State Machine.

Defines the State ABC and Context ABC following the State pattern.
OCP: adding a new state requires only a new class, no modification of existing code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orders.domain.entities import Order


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, from_state: str, action: str) -> None:
        self.from_state = from_state
        self.action = action
        super().__init__(f"Cannot perform '{action}' on order in state '{from_state}'.")


class OrderState(ABC):
    """Abstract base for all order states.

    Each concrete state implements only the transitions it allows;
    invalid transitions raise InvalidTransitionError by default.
    """

    def pay(self, ctx: Order) -> None:
        raise InvalidTransitionError(self.get_name(), "pay")

    def ship(self, ctx: Order) -> None:
        raise InvalidTransitionError(self.get_name(), "ship")

    def deliver(self, ctx: Order) -> None:
        raise InvalidTransitionError(self.get_name(), "deliver")

    def cancel(self, ctx: Order) -> None:
        raise InvalidTransitionError(self.get_name(), "cancel")

    def request_refund(self, ctx: Order) -> None:
        raise InvalidTransitionError(self.get_name(), "request_refund")

    def process_refund(self, ctx: Order) -> None:
        raise InvalidTransitionError(self.get_name(), "process_refund")

    @abstractmethod
    def get_name(self) -> str:
        """Return the canonical name of this state."""

    @abstractmethod
    def get_allowed_transitions(self) -> list[str]:
        """Return the list of allowed action names from this state."""
