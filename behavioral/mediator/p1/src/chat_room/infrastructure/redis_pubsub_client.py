"""Real Redis Pub/Sub client, built on redis.asyncio."""

from __future__ import annotations

from collections.abc import AsyncIterator

import redis.asyncio as redis


class RedisPubSubClient:
    """Wraps a `redis.asyncio.Redis` connection as a PubSubClient."""

    def __init__(self, redis_client: redis.Redis) -> None:
        self._client = redis_client

    async def publish(self, channel: str, message: str) -> None:
        await self._client.publish(channel, message)

    async def subscribe(self, channel: str) -> AsyncIterator[str]:
        pubsub = self._client.pubsub()
        await pubsub.subscribe(channel)
        try:
            async for event in pubsub.listen():
                if event["type"] == "message":
                    yield event["data"]
        finally:
            await pubsub.unsubscribe(channel)
