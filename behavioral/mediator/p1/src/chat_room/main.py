"""FastAPI application for the WebSocket Chat Room service.

Composition root: the only place that wires concrete Redis-backed
mediators (one per room) into the use cases.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from chat_room.application.use_cases import (
    JoinRoomUseCase,
    LeaveRoomUseCase,
    SendMessageUseCase,
)
from chat_room.domain.interfaces import ChatMediator
from chat_room.infrastructure.factory import build_mediator
from chat_room.infrastructure.websocket_participant import WebSocketChatParticipant

_mediators: dict[str, ChatMediator] = {}


async def get_mediator(room_id: str) -> ChatMediator:
    if room_id not in _mediators:
        mediator = build_mediator(room_id)
        await mediator.start_listening()
        _mediators[room_id] = mediator
    return _mediators[room_id]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    _mediators.clear()


app = FastAPI(
    title="WebSocket Chat Room — Mediator Pattern",
    description=(
        "Mediator pattern: ChatMediator=RedisChatMediator, "
        "Colleague=WebSocketChatParticipant. Participants never talk to "
        "each other directly, only through the mediator."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.websocket("/ws/rooms/{room_id}")
async def chat_room_websocket(websocket: WebSocket, room_id: str) -> None:
    await websocket.accept()

    mediator = await get_mediator(room_id)

    participant_id = str(uuid.uuid4())
    participant = WebSocketChatParticipant(participant_id, websocket)

    JoinRoomUseCase(mediator).execute(participant)
    send_use_case = SendMessageUseCase(mediator)

    try:
        while True:
            text = await websocket.receive_text()
            await send_use_case.execute(participant_id, text)
    except WebSocketDisconnect:
        pass
    finally:
        LeaveRoomUseCase(mediator).execute(participant)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
