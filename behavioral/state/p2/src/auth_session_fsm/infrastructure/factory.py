"""Composition helpers — builds the concrete Redis client from env vars."""

from __future__ import annotations

import os

from redis import Redis


def build_redis_client() -> Redis:
    return Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        db=int(os.environ.get("REDIS_DB", "0")),
    )
