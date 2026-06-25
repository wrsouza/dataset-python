"""Django views for the Queue Bridge.

Composition roots: the only place in the HTTP layer that builds concrete
QueueClient/MessageBroker pairs. Views depend on use cases (application
layer) and inject the wired QueueClient into them.

DIP: views call build_queue_client() — they never instantiate
TaskQueueClient or CeleryRedisBroker directly in business logic.
"""

from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from task_queue.application.use_cases import (
    CheckBrokerHealthUseCase,
    DequeueMessagesUseCase,
    EnqueueMessageUseCase,
)
from task_queue.infrastructure.client_factory import build_queue_client


@require_http_methods(["GET"])
def health_check(request: HttpRequest, broker_type: str) -> JsonResponse:
    """GET /queue/health/<broker_type>/

    Returns a JSON health-check result for the requested broker.
    Always 200 with is_healthy=true|false — monitoring tools parse the body.
    """
    try:
        client = build_queue_client("task", broker_type)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    use_case = CheckBrokerHealthUseCase(client=client)
    result = use_case.execute()
    return JsonResponse(result.to_dict(), status=200)


@csrf_exempt
@require_http_methods(["POST"])
def enqueue_message(
    request: HttpRequest, broker_type: str, client_type: str
) -> JsonResponse:
    """POST /queue/enqueue/<broker_type>/<client_type>/

    Body (JSON): {"queue_name": "orders", "payload": {...}}
    """
    try:
        client = build_queue_client(client_type, broker_type)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    try:
        body: dict[str, object] = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    queue_name = body.get("queue_name", "")
    if not isinstance(queue_name, str) or not queue_name.strip():
        return JsonResponse(
            {"error": "Field 'queue_name' is required and must be non-empty."},
            status=400,
        )

    payload_raw = body.get("payload")
    payload: dict[str, object] = payload_raw if isinstance(payload_raw, dict) else {}

    from task_queue.domain.entities import BrokerPublishError

    use_case = EnqueueMessageUseCase(client=client)
    try:
        result = use_case.execute(payload=payload, queue_name=queue_name)
    except BrokerPublishError as exc:
        return JsonResponse({"error": str(exc)}, status=422)

    return JsonResponse(result.to_dict(), status=201)


@require_http_methods(["GET"])
def dequeue_messages(
    request: HttpRequest, broker_type: str, queue_name: str
) -> JsonResponse:
    """GET /queue/dequeue/<broker_type>/<queue_name>/?max=1"""
    try:
        client = build_queue_client("task", broker_type)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    try:
        max_messages = int(request.GET.get("max", "1"))
    except ValueError:
        return JsonResponse({"error": "'max' must be an integer."}, status=400)

    from task_queue.domain.entities import BrokerConnectionError

    use_case = DequeueMessagesUseCase(client=client)
    try:
        result = use_case.execute(queue_name=queue_name, max_messages=max_messages)
    except BrokerConnectionError as exc:
        return JsonResponse({"error": str(exc)}, status=503)

    return JsonResponse(result.to_dict(), status=200)
