"""Unit tests for WebSocketChatParticipant."""

from __future__ import annotations

import pytest

from chat_room.domain.entities import ChatMessage
from chat_room.infrastructure.websocket_participant import WebSocketChatParticipant


class FakeWebSocket:
    def __init__(self) -> None:
        self.sent: list[dict[str, object]] = []

    async def send_json(self, data: dict[str, object]) -> None:
        self.sent.append(data)


@pytest.mark.asyncio
async def test_receive_sends_message_as_json() -> None:
    websocket = FakeWebSocket()
    participant = WebSocketChatParticipant("alice", websocket)

    message = ChatMessage(room_id="room-1", sender_id="bob", text="hi")
    await participant.receive(message)

    assert websocket.sent == [
        {
            "room_id": "room-1",
            "sender_id": "bob",
            "text": "hi",
            "sent_at": message.sent_at.isoformat(),
        }
    ]


def test_get_participant_id_returns_assigned_id() -> None:
    participant = WebSocketChatParticipant("alice", FakeWebSocket())

    assert participant.get_participant_id() == "alice"
