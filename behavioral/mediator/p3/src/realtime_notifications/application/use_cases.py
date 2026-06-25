"""Use cases orchestrating notification persistence and broadcast."""

from __future__ import annotations

from asgiref.sync import sync_to_async

from realtime_notifications.domain.entities import Notification
from realtime_notifications.domain.interfaces import (
    NotificationMediator,
    NotificationRepository,
)


class PublishNotificationUseCase:
    """Persists a notification and broadcasts it through the mediator."""

    def __init__(
        self, mediator: NotificationMediator, repository: NotificationRepository
    ) -> None:
        self._mediator = mediator
        self._repository = repository

    async def execute(self, group: str, message: dict[str, object]) -> Notification:
        notification = Notification(group=group, message=message)
        await sync_to_async(self._repository.save)(notification)
        await self._mediator.notify(group, message)
        return notification


class ListNotificationsUseCase:
    """Returns every notification ever sent to a group."""

    def __init__(self, repository: NotificationRepository) -> None:
        self._repository = repository

    def execute(self, group: str) -> list[Notification]:
        return self._repository.list_for_group(group)
