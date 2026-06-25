"""CancelledState — terminal state, order was cancelled."""

from __future__ import annotations

from orders.domain.interfaces import OrderState


class CancelledState(OrderState):
    """Order was cancelled; no further transitions are allowed."""

    def get_name(self) -> str:
        return "Cancelled"

    def get_allowed_transitions(self) -> list[str]:
        return []
