"""Abstractions for the Mediator pattern and the notification persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from realtime_notifications.domain.entities import Notification


class NotificationMediator(ABC):
    """The Mediator: routes a notification to every client subscribed to a group.

    Publishers (Django views) and subscribers (WebSocket consumers) never
    reference each other directly — both only ever talk to this mediator.
    """

    @abstractmethod
    async def notify(self, group: str, message: dict[str, object]) -> None:
        """Broadcast `message` to every client currently subscribed to `group`."""


class NotificationRepository(ABC):
    """Persistence boundary for notifications."""

    @abstractmethod
    def save(self, notification: Notification) -> None:
        """Persist a notification."""

    @abstractmethod
    def list_for_group(self, group: str) -> list[Notification]:
        """Return every notification ever sent to `group`, oldest first."""
