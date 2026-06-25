"""A ChatParticipant backed by a real FastAPI WebSocket connection."""

from __future__ import annotations

from typing import Protocol

from chat_room.domain.entities import ChatMessage
from chat_room.domain.interfaces import ChatParticipant


class WebSocketLike(Protocol):
    """Minimal FastAPI WebSocket contract this participant relies on."""

    async def send_json(self, data: dict[str, object]) -> None: ...


class WebSocketChatParticipant(ChatParticipant):
    """Delivers mediator-routed messages to a connected WebSocket client."""

    def __init__(self, participant_id: str, websocket: WebSocketLike) -> None:
        self._participant_id = participant_id
        self._websocket = websocket

    def get_participant_id(self) -> str:
        return self._participant_id

    async def receive(self, message: ChatMessage) -> None:
        await self._websocket.send_json(
            {
                "room_id": message.room_id,
                "sender_id": message.sender_id,
                "text": message.text,
                "sent_at": message.sent_at.isoformat(),
            }
        )
