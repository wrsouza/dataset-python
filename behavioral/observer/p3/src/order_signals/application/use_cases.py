"""Application use cases for the Django Signals System.

Each use case has a single responsibility and depends only on
abstractions (DIP) — `OrderSubject`, plus the two log repositories.
"""

from __future__ import annotations

from dataclasses import dataclass

from order_signals.domain.entities import OrderEvent
from order_signals.domain.interfaces import OrderSubject
from order_signals.infrastructure.repository import (
    DjangoAuditLogRepository,
    DjangoNotificationLogRepository,
    DjangoOrderRepository,
)


@dataclass
class CreateOrderInput:
    order_id: str
    total: float


class CreateOrderUseCase:
    """Creates an order and broadcasts the event to every subscribed observer.

    SRP: only handles order creation; has no knowledge of which observers
    are subscribed or what they do with the event.
    """

    def __init__(
        self, repository: DjangoOrderRepository, subject: OrderSubject
    ) -> None:
        self._repository = repository
        self._subject = subject

    def execute(self, data: CreateOrderInput) -> OrderEvent:
        self._repository.save(data.order_id, data.total, status="created")
        event = OrderEvent(order_id=data.order_id, status="created", total=data.total)
        self._subject.notify(event)
        return event


@dataclass
class UpdateOrderStatusInput:
    order_id: str
    status: str


class UpdateOrderStatusUseCase:
    """Updates an order's status and broadcasts the resulting event."""

    def __init__(
        self, repository: DjangoOrderRepository, subject: OrderSubject
    ) -> None:
        self._repository = repository
        self._subject = subject

    def execute(self, data: UpdateOrderStatusInput) -> OrderEvent:
        order = self._repository.find_by_id(data.order_id)
        total = order.total if order is not None else 0.0
        self._repository.save(data.order_id, total, status=data.status)
        event = OrderEvent(order_id=data.order_id, status=data.status, total=total)
        self._subject.notify(event)
        return event


class GetAuditLogUseCase:
    """Returns every audit log entry written for an order."""

    def __init__(self, repository: DjangoAuditLogRepository) -> None:
        self._repository = repository

    def execute(self, order_id: str) -> list[str]:
        return [entry.message for entry in self._repository.list_for_order(order_id)]


class GetNotificationLogUseCase:
    """Returns every notification logged for an order."""

    def __init__(self, repository: DjangoNotificationLogRepository) -> None:
        self._repository = repository

    def execute(self, order_id: str) -> list[str]:
        return [entry.message for entry in self._repository.list_for_order(order_id)]
