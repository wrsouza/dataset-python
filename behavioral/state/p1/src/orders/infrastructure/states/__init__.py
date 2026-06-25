"""Concrete order states."""

from orders.infrastructure.states.cancelled import CancelledState
from orders.infrastructure.states.delivered import DeliveredState
from orders.infrastructure.states.paid import PaidState
from orders.infrastructure.states.pending import PendingState
from orders.infrastructure.states.refund_requested import RefundRequestedState
from orders.infrastructure.states.refunded import RefundedState
from orders.infrastructure.states.shipped import ShippedState

__all__ = [
    "CancelledState",
    "DeliveredState",
    "PaidState",
    "PendingState",
    "RefundRequestedState",
    "RefundedState",
    "ShippedState",
]

STATE_MAP: dict[str, type] = {
    "Pending": PendingState,
    "Paid": PaidState,
    "Shipped": ShippedState,
    "Delivered": DeliveredState,
    "Cancelled": CancelledState,
    "RefundRequested": RefundRequestedState,
    "Refunded": RefundedState,
}
