"""HTTP views exposing the Django Signals System: create/update orders, logs."""

from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from order_signals.application.use_cases import (
    CreateOrderInput,
    CreateOrderUseCase,
    GetAuditLogUseCase,
    GetNotificationLogUseCase,
    UpdateOrderStatusInput,
    UpdateOrderStatusUseCase,
)
from order_signals.infrastructure.observers import (
    AuditLogObserver,
    NotificationObserver,
)
from order_signals.infrastructure.repository import (
    DjangoAuditLogRepository,
    DjangoNotificationLogRepository,
    DjangoOrderRepository,
)
from order_signals.infrastructure.signal_subject import DjangoSignalOrderSubject

# Wired once at module import time: `connect`/`disconnect` mutate Django's
# process-global signal dispatch table, so subscribing per-request would
# leak a duplicate receiver — and a duplicate audit/notification row —
# on every single HTTP call.
_subject = DjangoSignalOrderSubject()
_subject.subscribe(AuditLogObserver())
_subject.subscribe(NotificationObserver(channel="email"))


def _build_subject() -> DjangoSignalOrderSubject:
    """Return the process-wide subject, with both observers already wired."""
    return _subject


@csrf_exempt
@require_http_methods(["POST"])
def create_order(request: HttpRequest) -> JsonResponse:
    """POST /orders/ — create an order and notify all observers."""
    payload = json.loads(request.body or "{}")
    use_case = CreateOrderUseCase(DjangoOrderRepository(), _build_subject())
    event = use_case.execute(
        CreateOrderInput(order_id=payload["order_id"], total=payload["total"])
    )
    return JsonResponse(
        {"order_id": event.order_id, "status": event.status, "total": event.total},
        status=201,
    )


@csrf_exempt
@require_http_methods(["PUT"])
def update_order_status(request: HttpRequest, order_id: str) -> JsonResponse:
    """PUT /orders/<order_id>/status/ — update status and notify observers."""
    payload = json.loads(request.body or "{}")
    use_case = UpdateOrderStatusUseCase(DjangoOrderRepository(), _build_subject())
    event = use_case.execute(
        UpdateOrderStatusInput(order_id=order_id, status=payload["status"])
    )
    return JsonResponse(
        {"order_id": event.order_id, "status": event.status, "total": event.total}
    )


@require_http_methods(["GET"])
def order_audit_log(request: HttpRequest, order_id: str) -> JsonResponse:
    """GET /orders/<order_id>/audit/ — list audit entries for an order."""
    use_case = GetAuditLogUseCase(DjangoAuditLogRepository())
    return JsonResponse(use_case.execute(order_id), safe=False)


@require_http_methods(["GET"])
def order_notification_log(request: HttpRequest, order_id: str) -> JsonResponse:
    """GET /orders/<order_id>/notifications/ — list notifications for an order."""
    use_case = GetNotificationLogUseCase(DjangoNotificationLogRepository())
    return JsonResponse(use_case.execute(order_id), safe=False)
