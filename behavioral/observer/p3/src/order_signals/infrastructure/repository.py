"""Django ORM repository for orders and the two observer logs."""

from __future__ import annotations

from order_signals.django_app.models import (
    AuditLogEntryModel,
    NotificationLogModel,
    OrderModel,
)


class DjangoOrderRepository:
    def save(self, order_id: str, total: float, status: str) -> None:
        OrderModel.objects.update_or_create(
            order_id=order_id, defaults={"total": total, "status": status}
        )

    def find_by_id(self, order_id: str) -> OrderModel | None:
        try:
            return OrderModel.objects.get(order_id=order_id)
        except OrderModel.DoesNotExist:
            return None


class DjangoAuditLogRepository:
    def list_for_order(self, order_id: str) -> list[AuditLogEntryModel]:
        return list(AuditLogEntryModel.objects.filter(order_id=order_id))


class DjangoNotificationLogRepository:
    def list_for_order(self, order_id: str) -> list[NotificationLogModel]:
        return list(NotificationLogModel.objects.filter(order_id=order_id))
