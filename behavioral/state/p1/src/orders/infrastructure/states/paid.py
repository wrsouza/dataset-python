"""PaidState — payment received, awaiting shipment."""

from __future__ import annotations

from typing import TYPE_CHECKING

from orders.domain.interfaces import OrderState

if TYPE_CHECKING:
    from orders.domain.entities import Order


class PaidState(OrderState):
    """Payment confirmed; order can be shipped or cancelled."""

    def ship(self, ctx: Order) -> None:
        from orders.infrastructure.states.shipped import ShippedState  # noqa: PLC0415

        ctx.transition_to(ShippedState(), "ship")

    def cancel(self, ctx: Order) -> None:
        from orders.infrastructure.states.cancelled import (
            CancelledState,
        )  # noqa: PLC0415

        ctx.transition_to(CancelledState(), "cancel")

    def get_name(self) -> str:
        return "Paid"

    def get_allowed_transitions(self) -> list[str]:
        return ["ship", "cancel"]
