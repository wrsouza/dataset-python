"""Domain entities and value objects for the Notification domain."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DeliveryStatus(str, Enum):
    SENT = "sent"
    FAILED = "failed"
    QUEUED = "queued"


class Channel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


@dataclass(frozen=True)
class DeliveryResult:
    status: DeliveryStatus
    message_id: str
    channel: Channel
    error: str | None = None

    @property
    def is_successful(self) -> bool:
        return self.status == DeliveryStatus.SENT


@dataclass
class NotificationPayload:
    """Generic payload; each Notification subtype reads the keys it needs."""

    data: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:  # noqa: ANN401
        return self.data.get(key, default)


@dataclass(frozen=True)
class AlertPayload:
    severity: str
    message: str
    source: str


@dataclass(frozen=True)
class ReportPayload:
    report_name: str
    period: str
    summary: str
    download_url: str


@dataclass(frozen=True)
class WelcomePayload:
    user_name: str
    activation_link: str
