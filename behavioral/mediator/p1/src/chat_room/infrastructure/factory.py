"""Composition helpers for wiring the mediator to a real Redis instance."""

from __future__ import annotations

import os

import redis.asyncio as redis

from chat_room.infrastructure.redis_mediator import RedisChatMediator
from chat_room.infrastructure.redis_pubsub_client import RedisPubSubClient


def build_pubsub_client() -> RedisPubSubClient:
    """Build a real Redis Pub/Sub client from environment variables."""
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return RedisPubSubClient(redis.from_url(redis_url))


def build_mediator(room_id: str) -> RedisChatMediator:
    """Build a mediator for `room_id`, wired to a real Redis Pub/Sub client."""
    return RedisChatMediator(build_pubsub_client(), room_id)
