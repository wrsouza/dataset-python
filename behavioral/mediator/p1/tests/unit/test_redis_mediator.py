"""Unit tests for RedisChatMediator, using an in-memory FakePubSubClient."""

from __future__ import annotations

import asyncio

import pytest

from chat_room.domain.entities import ChatMessage
from chat_room.domain.interfaces import ChatParticipant
from chat_room.infrastructure.redis_mediator import RedisChatMediator
from tests.conftest import FakePubSubClient


class RecordingParticipant(ChatParticipant):
    def __init__(self, participant_id: str) -> None:
        self._participant_id = participant_id
        self.received: list[ChatMessage] = []
        self._message_arrived = asyncio.Event()

    def get_participant_id(self) -> str:
        return self._participant_id

    async def receive(self, message: ChatMessage) -> None:
        self.received.append(message)
        self._message_arrived.set()

    async def wait_for_message(self, timeout: float = 1.0) -> None:
        await asyncio.wait_for(self._message_arrived.wait(), timeout=timeout)
        self._message_arrived.clear()


async def _settle() -> None:
    await asyncio.sleep(0.05)


@pytest.mark.asyncio
async def test_send_delivers_to_every_other_registered_participant() -> None:
    mediator = RedisChatMediator(FakePubSubClient(), room_id="room-1")
    await mediator.start_listening()
    try:
        alice = RecordingParticipant("alice")
        bob = RecordingParticipant("bob")
        mediator.register(alice)
        mediator.register(bob)

        await mediator.send("alice", "hello")
        await bob.wait_for_message()

        assert len(bob.received) == 1
        assert bob.received[0].text == "hello"
        assert bob.received[0].sender_id == "alice"
    finally:
        await mediator.stop_listening()


@pytest.mark.asyncio
async def test_send_does_not_deliver_back_to_sender() -> None:
    mediator = RedisChatMediator(FakePubSubClient(), room_id="room-1")
    await mediator.start_listening()
    try:
        alice = RecordingParticipant("alice")
        mediator.register(alice)

        await mediator.send("alice", "hello")
        await _settle()

        assert alice.received == []
    finally:
        await mediator.stop_listening()


@pytest.mark.asyncio
async def test_unregistered_participant_receives_nothing() -> None:
    mediator = RedisChatMediator(FakePubSubClient(), room_id="room-1")
    await mediator.start_listening()
    try:
        alice = RecordingParticipant("alice")
        bob = RecordingParticipant("bob")
        mediator.register(alice)
        mediator.register(bob)
        mediator.unregister(bob)

        await mediator.send("alice", "hello")
        await _settle()

        assert bob.received == []
    finally:
        await mediator.stop_listening()


@pytest.mark.asyncio
async def test_two_mediators_sharing_a_pubsub_client_relay_messages() -> None:
    """Two server processes (here: two mediators) sharing the same Redis
    channel both deliver the message to their own local participants —
    the cross-process fan-out the real Redis-backed design relies on."""
    shared_client = FakePubSubClient()
    mediator_a = RedisChatMediator(shared_client, room_id="room-1")
    mediator_b = RedisChatMediator(shared_client, room_id="room-1")
    await mediator_a.start_listening()
    await mediator_b.start_listening()
    try:
        alice = RecordingParticipant("alice")
        bob = RecordingParticipant("bob")
        mediator_a.register(alice)
        mediator_b.register(bob)

        await mediator_a.send("alice", "hello from A")
        await bob.wait_for_message()

        assert len(bob.received) == 1
        assert bob.received[0].text == "hello from A"
    finally:
        await mediator_a.stop_listening()
        await mediator_b.stop_listening()
