"""Integration tests for NotificationConsumer using Channels' test communicator."""

from __future__ import annotations

import pytest
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator

from realtime_notifications.infrastructure.consumers import NotificationConsumer

pytestmark = [pytest.mark.asyncio, pytest.mark.django_db]


async def test_consumer_receives_group_broadcast() -> None:
    communicator = WebsocketCommunicator(
        NotificationConsumer.as_asgi(), "/ws/notifications/room-1/"
    )
    communicator.scope["url_route"] = {"kwargs": {"group": "room-1"}}
    connected, _ = await communicator.connect()
    assert connected

    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        "room-1",
        {"type": "notification.message", "message": {"text": "hello"}},
    )

    response = await communicator.receive_json_from()
    assert response == {"text": "hello"}

    await communicator.disconnect()


async def test_consumer_in_different_group_does_not_receive_broadcast() -> None:
    communicator = WebsocketCommunicator(
        NotificationConsumer.as_asgi(), "/ws/notifications/room-2/"
    )
    communicator.scope["url_route"] = {"kwargs": {"group": "room-2"}}
    connected, _ = await communicator.connect()
    assert connected

    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        "room-1",
        {"type": "notification.message", "message": {"text": "hello"}},
    )

    assert await communicator.receive_nothing(timeout=0.2)

    await communicator.disconnect()
