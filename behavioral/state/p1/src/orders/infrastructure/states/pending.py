"""PendingState — initial state for a new order."""

from __future__ import annotations

from typing import TYPE_CHECKING

from orders.domain.interfaces import OrderState

if TYPE_CHECKING:
    from orders.domain.entities import Order


class PendingState(OrderState):
    """Order has been created but payment has not been received."""

    def pay(self, ctx: Order) -> None:
        from orders.infrastructure.states.paid import PaidState  # noqa: PLC0415

        ctx.transition_to(PaidState(), "pay")

    def cancel(self, ctx: Order) -> None:
        from orders.infrastructure.states.cancelled import (
            CancelledState,
        )  # noqa: PLC0415

        ctx.transition_to(CancelledState(), "cancel")

    def get_name(self) -> str:
        return "Pending"

    def get_allowed_transitions(self) -> list[str]:
        return ["pay", "cancel"]
