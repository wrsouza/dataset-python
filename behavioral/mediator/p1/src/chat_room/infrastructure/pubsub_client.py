"""Abstraction over a Redis Pub/Sub client, so the mediator stays testable."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol


class PubSubClient(Protocol):
    """Minimal async Redis Pub/Sub contract the mediator relies on."""

    async def publish(self, channel: str, message: str) -> None: ...

    def subscribe(self, channel: str) -> AsyncIterator[str]: ...
