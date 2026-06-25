"""ConcreteObservers — independent reactions to the same OrderEvent.

OCP: a new reaction (e.g. a billing observer) is added by writing a
new class implementing OrderObserver and subscribing it, without
touching AuditLogObserver, NotificationObserver, or OrderSubject.
"""

from __future__ import annotations

from datetime import UTC, datetime

from order_signals.django_app.models import AuditLogEntryModel, NotificationLogModel
from order_signals.domain.entities import OrderEvent
from order_signals.domain.interfaces import OrderObserver


class AuditLogObserver(OrderObserver):
    """Writes a compliance audit trail entry for every order event."""

    def on_order_event(self, event: OrderEvent) -> None:
        AuditLogEntryModel.objects.create(
            order_id=event.order_id,
            message=f"Order {event.order_id} changed to status '{event.status}'",
            created_at=datetime.now(UTC),
        )


class NotificationObserver(OrderObserver):
    """Simulates sending a customer notification for every order event."""

    def __init__(self, channel: str = "email") -> None:
        self._channel = channel

    def on_order_event(self, event: OrderEvent) -> None:
        NotificationLogModel.objects.create(
            order_id=event.order_id,
            channel=self._channel,
            message=f"Your order {event.order_id} is now '{event.status}'",
            created_at=datetime.now(UTC),
        )
