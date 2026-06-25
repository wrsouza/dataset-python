"""Unit tests for Django Signals System use cases."""

from __future__ import annotations

import pytest

from order_signals.application.use_cases import (
    CreateOrderInput,
    CreateOrderUseCase,
    UpdateOrderStatusInput,
    UpdateOrderStatusUseCase,
)
from order_signals.domain.entities import OrderEvent
from order_signals.domain.interfaces import OrderObserver, OrderSubject
from order_signals.infrastructure.repository import DjangoOrderRepository

pytestmark = pytest.mark.django_db


class FakeOrderSubject(OrderSubject):
    def __init__(self) -> None:
        self.notified: list[OrderEvent] = []

    def subscribe(self, observer: OrderObserver) -> None:
        raise NotImplementedError

    def unsubscribe(self, observer: OrderObserver) -> None:
        raise NotImplementedError

    def notify(self, event: OrderEvent) -> None:
        self.notified.append(event)


def test_create_order_persists_and_notifies() -> None:
    subject = FakeOrderSubject()
    use_case = CreateOrderUseCase(DjangoOrderRepository(), subject)

    event = use_case.execute(CreateOrderInput(order_id="o1", total=99.5))

    assert event.status == "created"
    assert subject.notified == [event]
    assert DjangoOrderRepository().find_by_id("o1") is not None


def test_update_order_status_persists_and_notifies() -> None:
    subject = FakeOrderSubject()
    repository = DjangoOrderRepository()
    CreateOrderUseCase(repository, subject).execute(
        CreateOrderInput(order_id="o1", total=99.5)
    )

    use_case = UpdateOrderStatusUseCase(repository, subject)
    event = use_case.execute(UpdateOrderStatusInput(order_id="o1", status="shipped"))

    assert event.status == "shipped"
    assert event.total == 99.5
    assert subject.notified[-1] == event


def test_update_order_status_for_unknown_order_defaults_total_to_zero() -> None:
    subject = FakeOrderSubject()
    use_case = UpdateOrderStatusUseCase(DjangoOrderRepository(), subject)

    event = use_case.execute(
        UpdateOrderStatusInput(order_id="unknown", status="cancelled")
    )

    assert event.total == 0.0
