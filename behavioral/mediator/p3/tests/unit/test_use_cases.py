"""Unit tests for PublishNotificationUseCase and ListNotificationsUseCase."""

from __future__ import annotations

import pytest

from realtime_notifications.application.use_cases import (
    ListNotificationsUseCase,
    PublishNotificationUseCase,
)
from realtime_notifications.domain.entities import Notification
from realtime_notifications.domain.interfaces import (
    NotificationMediator,
    NotificationRepository,
)


class FakeMediator(NotificationMediator):
    def __init__(self) -> None:
        self.notified: list[tuple[str, dict[str, object]]] = []

    async def notify(self, group: str, message: dict[str, object]) -> None:
        self.notified.append((group, message))


class InMemoryNotificationRepository(NotificationRepository):
    def __init__(self) -> None:
        self._notifications: list[Notification] = []

    def save(self, notification: Notification) -> None:
        self._notifications.append(notification)

    def list_for_group(self, group: str) -> list[Notification]:
        return [n for n in self._notifications if n.group == group]


@pytest.mark.asyncio
async def test_publish_persists_and_notifies() -> None:
    mediator = FakeMediator()
    repository = InMemoryNotificationRepository()
    use_case = PublishNotificationUseCase(mediator, repository)

    notification = await use_case.execute("room-1", {"text": "hi"})

    assert mediator.notified == [("room-1", {"text": "hi"})]
    assert repository.list_for_group("room-1") == [notification]


def test_list_notifications_filters_by_group() -> None:
    repository = InMemoryNotificationRepository()
    repository.save(Notification(group="room-1", message={"text": "a"}))
    repository.save(Notification(group="room-2", message={"text": "b"}))

    results = ListNotificationsUseCase(repository).execute("room-1")

    assert [n.message for n in results] == [{"text": "a"}]
