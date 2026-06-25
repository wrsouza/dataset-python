"""Shared pytest fixtures for the chat room mediator tests."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator


class FakePubSubClient:
    """An in-memory PubSubClient backed by asyncio.Queue, one per channel.

    `publish` delivers to every active subscriber of that channel,
    mirroring real Redis Pub/Sub fan-out semantics closely enough for
    tests, without needing a real Redis server.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[str]]] = {}

    async def publish(self, channel: str, message: str) -> None:
        for queue in self._subscribers.get(channel, []):
            await queue.put(message)

    async def subscribe(self, channel: str) -> AsyncIterator[str]:
        queue: asyncio.Queue[str] = asyncio.Queue()
        self._subscribers.setdefault(channel, []).append(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            self._subscribers[channel].remove(queue)
