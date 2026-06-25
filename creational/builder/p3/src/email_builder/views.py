"""Django views for the Email Builder API."""

from __future__ import annotations

import json
import os

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from email_builder.application.use_cases import SendCampaignEmailUseCase
from email_builder.infrastructure.ses_sender import SESEmailSender
from email_builder.models import EmailLog


def _get_sender() -> SESEmailSender:
    endpoint = os.getenv("AWS_ENDPOINT_URL") or None
    return SESEmailSender(endpoint_url=endpoint)


@method_decorator(csrf_exempt, name="dispatch")
class SendEmailView(View):
    """POST /emails/<template_type> — build and send an email."""

    def post(self, request: HttpRequest, template_type: str) -> JsonResponse:
        try:
            data: dict[str, object] = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        sender = _get_sender()
        use_case = SendCampaignEmailUseCase(sender)

        recipient: str = str(data.get("recipient", ""))
        if not recipient:
            return JsonResponse({"error": "recipient is required"}, status=400)

        if template_type == "welcome":
            result = use_case.send_welcome(
                recipient=recipient,
                user_name=str(data.get("user_name", "User")),
            )
        elif template_type == "password_reset":
            result = use_case.send_password_reset(
                recipient=recipient,
                reset_url=str(data.get("reset_url", "")),
            )
        elif template_type == "order_confirmation":
            total_raw = data.get("total", 0.0)
            total = (
                float(total_raw) if isinstance(total_raw, (int, float, str)) else 0.0
            )
            result = use_case.send_order_confirmation(
                recipient=recipient,
                order_id=str(data.get("order_id", "")),
                items=data.get("items", []),  # type: ignore[arg-type]
                total=total,
            )
        else:
            return JsonResponse(
                {"error": f"Unknown template type: {template_type}"}, status=404
            )

        EmailLog.objects.create(
            template_type=result.template_type.value,
            recipient=result.recipient,
            status="sent" if result.success else "failed",
            message_id=result.message_id,
            error_message=result.error or "",
        )

        if result.success:
            return JsonResponse({"message_id": result.message_id, "status": "sent"})
        return JsonResponse({"error": result.error, "status": "failed"}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class EmailLogListView(View):
    """GET /emails/logs — list recent email logs."""

    def get(self, request: HttpRequest) -> JsonResponse:
        logs = list(
            EmailLog.objects.values(
                "id", "template_type", "recipient", "sent_at", "status"
            )[:50]
        )
        return JsonResponse({"logs": logs, "count": len(logs)})
