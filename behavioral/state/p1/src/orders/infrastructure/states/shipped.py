"""ShippedState — order dispatched to carrier."""

from __future__ import annotations

from typing import TYPE_CHECKING

from orders.domain.interfaces import OrderState

if TYPE_CHECKING:
    from orders.domain.entities import Order


class ShippedState(OrderState):
    """Order is in transit; only delivery is the next valid step."""

    def deliver(self, ctx: Order) -> None:
        from orders.infrastructure.states.delivered import (
            DeliveredState,
        )  # noqa: PLC0415

        ctx.transition_to(DeliveredState(), "deliver")

    def get_name(self) -> str:
        return "Shipped"

    def get_allowed_transitions(self) -> list[str]:
        return ["deliver"]
