"""Redis Pub/Sub-backed implementation of ChatMediator.

Publishing and listening both go through the same Redis channel, so
every server process running this mediator (and subscribed to the same
channel) converges on the same message order — the Mediator pattern
applied across process boundaries via Redis instead of in-memory only.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime

from chat_room.domain.entities import ChatMessage
from chat_room.domain.interfaces import ChatMediator, ChatParticipant
from chat_room.infrastructure.pubsub_client import PubSubClient


class RedisChatMediator(ChatMediator):
    """Routes chat messages between locally registered participants via Redis."""

    def __init__(self, client: PubSubClient, room_id: str) -> None:
        self._client = client
        self._room_id = room_id
        self._channel = f"chat-room:{room_id}"
        self._participants: dict[str, ChatParticipant] = {}
        self._listener_task: asyncio.Task[None] | None = None

    def register(self, participant: ChatParticipant) -> None:
        self._participants[participant.get_participant_id()] = participant

    def unregister(self, participant: ChatParticipant) -> None:
        self._participants.pop(participant.get_participant_id(), None)

    async def send(self, sender_id: str, text: str) -> None:
        message = ChatMessage(room_id=self._room_id, sender_id=sender_id, text=text)
        await self._client.publish(self._channel, self._serialize(message))

    async def start_listening(self) -> None:
        """Start consuming the Redis channel and dispatching to local participants.

        Yields control once after scheduling the listener task so that its
        subscription is registered with the Pub/Sub client before this
        call returns — otherwise a `send()` immediately following this
        call could race the subscription and be missed.
        """
        self._listener_task = asyncio.create_task(self._listen())
        await asyncio.sleep(0)

    async def stop_listening(self) -> None:
        if self._listener_task is not None:
            self._listener_task.cancel()
            self._listener_task = None

    async def _listen(self) -> None:
        async for raw in self._client.subscribe(self._channel):
            message = self._deserialize(raw)
            for participant_id, participant in list(self._participants.items()):
                if participant_id != message.sender_id:
                    await participant.receive(message)

    @staticmethod
    def _serialize(message: ChatMessage) -> str:
        return json.dumps(
            {
                "room_id": message.room_id,
                "sender_id": message.sender_id,
                "text": message.text,
                "sent_at": message.sent_at.isoformat(),
            }
        )

    @staticmethod
    def _deserialize(raw: str) -> ChatMessage:
        data = json.loads(raw)
        return ChatMessage(
            room_id=data["room_id"],
            sender_id=data["sender_id"],
            text=data["text"],
            sent_at=datetime.fromisoformat(data["sent_at"]),
        )
