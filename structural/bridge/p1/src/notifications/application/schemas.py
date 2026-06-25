"""Pydantic v2 request/response schemas for the FastAPI layer."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, EmailStr, Field

from notifications.domain.entities import Channel, DeliveryResult, DeliveryStatus


class AlertRequest(BaseModel):
    recipient: str = Field(..., description="Recipient address (email/phone/token)")
    channel: Channel = Field(Channel.EMAIL, description="Delivery channel")
    severity: str = Field("INFO", description="Alert severity level")
    message: str = Field(..., description="Alert message body")
    source: str = Field("system", description="Alert source system")


class ReportRequest(BaseModel):
    recipient: str
    channel: Channel = Channel.EMAIL
    report_name: str
    period: str
    summary: str
    download_url: str = ""


class WelcomeRequest(BaseModel):
    recipient: str
    channel: Channel = Channel.EMAIL
    user_name: str
    activation_link: str


class DeliveryResponse(BaseModel):
    status: DeliveryStatus
    message_id: str
    channel: Channel
    error: str | None = None

    @classmethod
    def from_result(cls, result: DeliveryResult) -> DeliveryResponse:
        return cls(
            status=result.status,
            message_id=result.message_id,
            channel=result.channel,
            error=result.error,
        )
