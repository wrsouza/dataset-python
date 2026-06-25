"""WebSocket consumer: the subscriber side of the notification mediator."""

from __future__ import annotations

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):  # type: ignore[misc]
    """Joins a group on connect and forwards mediator broadcasts to the client."""

    async def connect(self) -> None:
        self.group_name = self.scope["url_route"]["kwargs"]["group"]
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code: int) -> None:
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notification_message(self, event: dict[str, object]) -> None:
        """Handle a `notification.message` group event by forwarding it."""
        await self.send_json(event["message"])
