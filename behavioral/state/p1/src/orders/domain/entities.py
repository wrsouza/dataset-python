"""Domain entities for the Order State Machine."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class OrderItem:
    product_id: str
    name: str
    quantity: int
    unit_price: float

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class StateTransitionRecord:
    from_state: str
    to_state: str
    action: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Order:
    """Context in the State pattern.

    Delegates all behaviour to the current _state object.
    """

    from orders.domain.interfaces import (
        OrderState,
    )  # noqa: PLC0415 — local import avoids cycle

    order_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    items: list[OrderItem] = field(default_factory=list)
    history: list[StateTransitionRecord] = field(default_factory=list)
    _state: OrderState = field(init=False)

    def __post_init__(self) -> None:
        from orders.infrastructure.states.pending import PendingState  # noqa: PLC0415

        self._state = PendingState()

    # ── State delegation ────────────────────────────────────────────────────────

    def pay(self) -> None:
        self._state.pay(self)

    def ship(self) -> None:
        self._state.ship(self)

    def deliver(self) -> None:
        self._state.deliver(self)

    def cancel(self) -> None:
        self._state.cancel(self)

    def request_refund(self) -> None:
        self._state.request_refund(self)

    def process_refund(self) -> None:
        self._state.process_refund(self)

    # ── State accessors ─────────────────────────────────────────────────────────

    def get_current_state_name(self) -> str:
        return self._state.get_name()

    def get_allowed_transitions(self) -> list[str]:
        return self._state.get_allowed_transitions()

    def transition_to(self, new_state: OrderState, action: str) -> None:
        """Record the transition and swap the current state."""
        record = StateTransitionRecord(
            from_state=self._state.get_name(),
            to_state=new_state.get_name(),
            action=action,
        )
        self.history.append(record)
        self._state = new_state

    # ── Computed properties ──────────────────────────────────────────────────────

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)
