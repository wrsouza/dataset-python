"""Unit tests for the join/leave/send use cases."""

from __future__ import annotations

import asyncio

import pytest

from chat_room.application.use_cases import (
    JoinRoomUseCase,
    LeaveRoomUseCase,
    SendMessageUseCase,
)
from chat_room.infrastructure.redis_mediator import RedisChatMediator
from tests.conftest import FakePubSubClient
from tests.unit.test_redis_mediator import RecordingParticipant


@pytest.mark.asyncio
async def test_join_then_send_delivers_message() -> None:
    mediator = RedisChatMediator(FakePubSubClient(), room_id="room-1")
    await mediator.start_listening()
    try:
        alice = RecordingParticipant("alice")
        bob = RecordingParticipant("bob")
        JoinRoomUseCase(mediator).execute(alice)
        JoinRoomUseCase(mediator).execute(bob)

        await SendMessageUseCase(mediator).execute("alice", "hello")
        await bob.wait_for_message()

        assert bob.received[0].text == "hello"
    finally:
        await mediator.stop_listening()


@pytest.mark.asyncio
async def test_leave_room_stops_future_delivery() -> None:
    mediator = RedisChatMediator(FakePubSubClient(), room_id="room-1")
    await mediator.start_listening()
    try:
        alice = RecordingParticipant("alice")
        bob = RecordingParticipant("bob")
        JoinRoomUseCase(mediator).execute(alice)
        JoinRoomUseCase(mediator).execute(bob)
        LeaveRoomUseCase(mediator).execute(bob)

        await SendMessageUseCase(mediator).execute("alice", "hello")
        await asyncio.sleep(0.05)

        assert bob.received == []
    finally:
        await mediator.stop_listening()
