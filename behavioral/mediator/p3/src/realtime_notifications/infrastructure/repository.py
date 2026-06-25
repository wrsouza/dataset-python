"""Django ORM-backed implementation of NotificationRepository."""

from __future__ import annotations

from realtime_notifications.domain.entities import Notification
from realtime_notifications.domain.interfaces import NotificationRepository
from realtime_notifications.infrastructure.models import NotificationModel


class DjangoNotificationRepository(NotificationRepository):
    """Persists notifications via the Django ORM."""

    def save(self, notification: Notification) -> None:
        NotificationModel.objects.create(
            group=notification.group,
            message=notification.message,
            created_at=notification.created_at,
        )

    def list_for_group(self, group: str) -> list[Notification]:
        return [
            Notification(
                group=row.group, message=row.message, created_at=row.created_at
            )
            for row in NotificationModel.objects.filter(group=group)
        ]
