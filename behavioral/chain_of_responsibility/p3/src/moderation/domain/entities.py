"""Core entities for the content moderation domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class ModerationStatus(StrEnum):
    """Final outcome of a content submission going through the pipeline."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ModerationStep:
    """A single hop the submission made through the moderation chain."""

    handler_name: str
    action: ModerationStatus
    reason: str
    handled_at: datetime


@dataclass
class ContentSubmission:
    """A piece of user-generated content moving through the moderation chain."""

    submission_id: str
    author: str
    text: str
    image_bytes: bytes | None = None
    status: ModerationStatus = ModerationStatus.PENDING
    history: list[ModerationStep] = field(default_factory=list)

    def record_step(self, step: ModerationStep) -> None:
        """Append a moderation step and update the submission status."""
        self.history.append(step)
        self.status = step.action
