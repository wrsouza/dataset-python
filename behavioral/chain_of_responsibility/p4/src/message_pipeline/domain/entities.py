"""Core entities for the message processing pipeline domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class ProcessingStatus(StrEnum):
    """Final outcome of a message going through the processing chain."""

    PENDING = "pending"
    PROCESSED = "processed"
    REJECTED = "rejected"


@dataclass
class ProcessingStep:
    """A single hop the message made through the handler chain."""

    handler_name: str
    status: ProcessingStatus
    reason: str
    handled_at: datetime


@dataclass
class IncomingMessage:
    """A message consumed from the broker, moving through the processing chain."""

    message_id: str
    payload: dict[str, object]
    status: ProcessingStatus = ProcessingStatus.PENDING
    history: list[ProcessingStep] = field(default_factory=list)

    def record_step(self, step: ProcessingStep) -> None:
        """Append a processing step and update the message status."""
        self.history.append(step)
        self.status = step.status
