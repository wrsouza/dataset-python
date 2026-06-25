"""Unit tests for Order state transitions."""

from __future__ import annotations

import pytest

from orders.domain.entities import Order, OrderItem
from orders.domain.interfaces import InvalidTransitionError


def make_order() -> Order:
    return Order(items=[OrderItem("p1", "Widget", 2, 9.99)])


# ── Valid transition path ────────────────────────────────────────────────────


def test_initial_state_is_pending() -> None:
    assert make_order().get_current_state_name() == "Pending"


def test_pending_to_paid() -> None:
    order = make_order()
    order.pay()
    assert order.get_current_state_name() == "Paid"


def test_paid_to_shipped() -> None:
    order = make_order()
    order.pay()
    order.ship()
    assert order.get_current_state_name() == "Shipped"


def test_shipped_to_delivered() -> None:
    order = make_order()
    order.pay()
    order.ship()
    order.deliver()
    assert order.get_current_state_name() == "Delivered"


def test_delivered_to_refund_requested() -> None:
    order = make_order()
    order.pay()
    order.ship()
    order.deliver()
    order.request_refund()
    assert order.get_current_state_name() == "RefundRequested"


def test_refund_requested_to_refunded() -> None:
    order = make_order()
    order.pay()
    order.ship()
    order.deliver()
    order.request_refund()
    order.process_refund()
    assert order.get_current_state_name() == "Refunded"


def test_pending_to_cancelled() -> None:
    order = make_order()
    order.cancel()
    assert order.get_current_state_name() == "Cancelled"


def test_paid_to_cancelled() -> None:
    order = make_order()
    order.pay()
    order.cancel()
    assert order.get_current_state_name() == "Cancelled"


# ── History tracking ─────────────────────────────────────────────────────────


def test_history_records_transitions() -> None:
    order = make_order()
    order.pay()
    order.ship()
    assert len(order.history) == 2
    assert order.history[0].from_state == "Pending"
    assert order.history[0].to_state == "Paid"
    assert order.history[1].from_state == "Paid"
    assert order.history[1].to_state == "Shipped"


# ── Invalid transitions ───────────────────────────────────────────────────────


def test_pending_cannot_ship() -> None:
    with pytest.raises(InvalidTransitionError) as exc_info:
        make_order().ship()
    assert "Pending" in str(exc_info.value)
    assert "ship" in str(exc_info.value)


def test_pending_cannot_deliver() -> None:
    with pytest.raises(InvalidTransitionError):
        make_order().deliver()


def test_pending_cannot_request_refund() -> None:
    with pytest.raises(InvalidTransitionError):
        make_order().request_refund()


def test_shipped_cannot_cancel() -> None:
    order = make_order()
    order.pay()
    order.ship()
    with pytest.raises(InvalidTransitionError):
        order.cancel()


def test_delivered_cannot_cancel() -> None:
    order = make_order()
    order.pay()
    order.ship()
    order.deliver()
    with pytest.raises(InvalidTransitionError):
        order.cancel()


def test_cancelled_cannot_pay() -> None:
    order = make_order()
    order.cancel()
    with pytest.raises(InvalidTransitionError):
        order.pay()


def test_refunded_is_terminal() -> None:
    order = make_order()
    order.pay()
    order.ship()
    order.deliver()
    order.request_refund()
    order.process_refund()
    with pytest.raises(InvalidTransitionError):
        order.cancel()


# ── Allowed transitions list ─────────────────────────────────────────────────


def test_pending_allowed_transitions() -> None:
    assert set(make_order().get_allowed_transitions()) == {"pay", "cancel"}


def test_paid_allowed_transitions() -> None:
    order = make_order()
    order.pay()
    assert set(order.get_allowed_transitions()) == {"ship", "cancel"}


def test_cancelled_allowed_transitions() -> None:
    order = make_order()
    order.cancel()
    assert order.get_allowed_transitions() == []


# ── Total calculation ─────────────────────────────────────────────────────────


def test_order_total() -> None:
    order = Order(
        items=[
            OrderItem("p1", "Widget", 2, 10.0),
            OrderItem("p2", "Gadget", 1, 5.0),
        ]
    )
    assert order.total == 25.0
