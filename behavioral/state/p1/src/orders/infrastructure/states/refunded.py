"""RefundedState — terminal state, refund has been issued."""

from __future__ import annotations

from orders.domain.interfaces import OrderState


class RefundedState(OrderState):
    """Refund was processed successfully; no further transitions."""

    def get_name(self) -> str:
        return "Refunded"

    def get_allowed_transitions(self) -> list[str]:
        return []
