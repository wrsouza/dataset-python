"""Unit tests for ChannelsNotificationMediator using a fake channel layer."""

from __future__ import annotations

import pytest

from realtime_notifications.infrastructure.channel_mediator import (
    ChannelsNotificationMediator,
)


class FakeChannelLayer:
    def __init__(self) -> None:
        self.sent: list[tuple[str, dict[str, object]]] = []

    async def group_send(self, group: str, message: dict[str, object]) -> None:
        self.sent.append((group, message))


@pytest.mark.asyncio
async def test_notify_sends_a_notification_message_event() -> None:
    layer = FakeChannelLayer()
    mediator = ChannelsNotificationMediator(layer)

    await mediator.notify("room-1", {"text": "hello"})

    [(group, event)] = layer.sent
    assert group == "room-1"
    assert event == {"type": "notification.message", "message": {"text": "hello"}}
