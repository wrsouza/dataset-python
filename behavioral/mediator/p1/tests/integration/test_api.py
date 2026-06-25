"""Integration tests for the chat room FastAPI app, with a fake mediator factory."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import chat_room.main as main_module
from chat_room.infrastructure.redis_mediator import RedisChatMediator
from tests.conftest import FakePubSubClient


@pytest.fixture(autouse=True)
def _fake_mediator_factory(monkeypatch: pytest.MonkeyPatch) -> None:
    shared_client = FakePubSubClient()

    def fake_build_mediator(room_id: str) -> RedisChatMediator:
        return RedisChatMediator(shared_client, room_id)

    monkeypatch.setattr(main_module, "build_mediator", fake_build_mediator)
    main_module._mediators.clear()


def test_health_check() -> None:
    client = TestClient(main_module.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_two_clients_in_same_room_relay_messages() -> None:
    client = TestClient(main_module.app)

    with client.websocket_connect("/ws/rooms/room-1") as alice_ws:
        with client.websocket_connect("/ws/rooms/room-1") as bob_ws:
            alice_ws.send_text("hello bob")
            received = bob_ws.receive_json()

    assert received["text"] == "hello bob"


def test_message_reaches_every_other_participant_in_the_room() -> None:
    client = TestClient(main_module.app)

    with client.websocket_connect("/ws/rooms/room-2") as alice_ws:
        with client.websocket_connect("/ws/rooms/room-2") as bob_ws:
            with client.websocket_connect("/ws/rooms/room-2") as carol_ws:
                alice_ws.send_text("hello everyone")
                bob_message = bob_ws.receive_json()
                carol_message = carol_ws.receive_json()

    assert bob_message["text"] == "hello everyone"
    assert carol_message["text"] == "hello everyone"
