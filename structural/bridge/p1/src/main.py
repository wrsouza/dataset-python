"""FastAPI application — Notification Bridge.

Composition root: wires the Bridge pattern components and exposes
REST endpoints for each notification type.
"""
from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException, status

from notifications.application.schemas import (
    AlertRequest,
    DeliveryResponse,
    ReportRequest,
    WelcomeRequest,
)
from notifications.application.use_cases import SendNotificationUseCase
from notifications.domain.entities import DeliveryStatus, NotificationPayload

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Notification Bridge",
    description=(
        "Bridge pattern demo: notification types × delivery channels. "
        "Any type (Alert, Report, Welcome) works with any channel (Email, SMS, Push)."
    ),
    version="1.0.0",
)

# Composition root — inject concrete config from environment.
_use_case = SendNotificationUseCase(
    email_sender_address=os.getenv("SES_SENDER", "noreply@example.com"),
    ses_endpoint_url=os.getenv("LOCALSTACK_ENDPOINT", "http://localstack:4566"),
)


def _assert_delivered(result: DeliveryResponse) -> None:
    if result.status == DeliveryStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Delivery failed: {result.error}",
        )


@app.post("/notifications/alert", response_model=DeliveryResponse, status_code=201)
def send_alert(request: AlertRequest) -> DeliveryResponse:
    """Send an alert notification via the chosen channel."""
    payload = NotificationPayload(
        data={
            "severity": request.severity,
            "message": request.message,
            "source": request.source,
        }
    )
    result = _use_case.send_alert(request.recipient, request.channel, payload)
    response = DeliveryResponse.from_result(result)
    _assert_delivered(response)
    return response


@app.post("/notifications/report", response_model=DeliveryResponse, status_code=201)
def send_report(request: ReportRequest) -> DeliveryResponse:
    """Send a report-ready notification via the chosen channel."""
    payload = NotificationPayload(
        data={
            "report_name": request.report_name,
            "period": request.period,
            "summary": request.summary,
            "download_url": request.download_url,
        }
    )
    result = _use_case.send_report(request.recipient, request.channel, payload)
    response = DeliveryResponse.from_result(result)
    _assert_delivered(response)
    return response


@app.post("/notifications/welcome", response_model=DeliveryResponse, status_code=201)
def send_welcome(request: WelcomeRequest) -> DeliveryResponse:
    """Send a welcome notification via the chosen channel."""
    payload = NotificationPayload(
        data={
            "user_name": request.user_name,
            "activation_link": request.activation_link,
        }
    )
    result = _use_case.send_welcome(request.recipient, request.channel, payload)
    response = DeliveryResponse.from_result(result)
    _assert_delivered(response)
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
