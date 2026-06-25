"""Core entities for the Kafka stream iteration domain."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StreamMessage:
    """A single Kafka record — the element type this Iterator traverses."""

    key: str | None
    value: dict[str, object]
    offset: int
    partition: int


@dataclass(frozen=True)
class StreamSummary:
    """Aggregate statistics computed by draining the currently available messages."""

    message_count: int
    total_amount: float
