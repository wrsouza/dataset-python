"""Django Channels-backed implementation of NotificationMediator.

Delegates the actual fan-out to the configured channel layer (in-memory
for tests, Redis-backed in production) — `group_send` is what makes a
notification published from an HTTP view reach every WebSocket consumer
subscribed to that group, possibly in a different worker process.
"""

from __future__ import annotations

from typing import Protocol

from realtime_notifications.domain.interfaces import NotificationMediator


class ChannelLayerLike(Protocol):
    """Minimal channels.layers contract this mediator relies on."""

    async def group_send(self, group: str, message: dict[str, object]) -> None: ...


class ChannelsNotificationMediator(NotificationMediator):
    """Broadcasts notifications to a Channels group."""

    def __init__(self, channel_layer: ChannelLayerLike) -> None:
        self._channel_layer = channel_layer

    async def notify(self, group: str, message: dict[str, object]) -> None:
        await self._channel_layer.group_send(
            group, {"type": "notification.message", "message": message}
        )
