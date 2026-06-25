"""Domain entities for the Email Builder."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class TemplateType(StrEnum):
    WELCOME = "welcome"
    PASSWORD_RESET = "password_reset"  # noqa: S105 — template name, not a secret
    ORDER_CONFIRMATION = "order_confirmation"


@dataclass
class Attachment:
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"


@dataclass
class Email:
    """Product: a fully constructed transactional email."""

    subject: str
    from_address: str
    to_addresses: list[str]
    html_body: str
    text_body: str
    template_type: TemplateType = TemplateType.WELCOME
    attachments: list[Attachment] = field(default_factory=list)
    reply_to: str | None = None


@dataclass
class SendResult:
    """Result of an SES send operation."""

    message_id: str
    recipient: str
    template_type: TemplateType
    success: bool
    error: str | None = None
