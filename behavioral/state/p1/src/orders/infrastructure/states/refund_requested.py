"""RefundRequestedState — customer has opened a refund request."""

from __future__ import annotations

from typing import TYPE_CHECKING

from orders.domain.interfaces import OrderState

if TYPE_CHECKING:
    from orders.domain.entities import Order


class RefundRequestedState(OrderState):
    """Refund is under review; can only be processed (approved)."""

    def process_refund(self, ctx: Order) -> None:
        from orders.infrastructure.states.refunded import RefundedState  # noqa: PLC0415

        ctx.transition_to(RefundedState(), "process_refund")

    def get_name(self) -> str:
        return "RefundRequested"

    def get_allowed_transitions(self) -> list[str]:
        return ["process_refund"]
