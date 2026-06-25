"""DeliveredState — order received by the customer."""

from __future__ import annotations

from typing import TYPE_CHECKING

from orders.domain.interfaces import OrderState

if TYPE_CHECKING:
    from orders.domain.entities import Order


class DeliveredState(OrderState):
    """Customer has received the order; refund can be requested."""

    def request_refund(self, ctx: Order) -> None:
        from orders.infrastructure.states.refund_requested import (  # noqa: PLC0415
            RefundRequestedState,
        )

        ctx.transition_to(RefundRequestedState(), "request_refund")

    def get_name(self) -> str:
        return "Delivered"

    def get_allowed_transitions(self) -> list[str]:
        return ["request_refund"]
