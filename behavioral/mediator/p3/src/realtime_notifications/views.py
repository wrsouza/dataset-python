"""HTTP views exposing the notification mediator: publish and list."""

from __future__ import annotations

import json

from channels.layers import get_channel_layer
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from realtime_notifications.application.use_cases import (
    ListNotificationsUseCase,
    PublishNotificationUseCase,
)
from realtime_notifications.domain.entities import Notification
from realtime_notifications.infrastructure.channel_mediator import (
    ChannelsNotificationMediator,
)
from realtime_notifications.infrastructure.repository import (
    DjangoNotificationRepository,
)


def _notification_to_dict(notification: Notification) -> dict[str, object]:
    return {
        "group": notification.group,
        "message": notification.message,
        "created_at": notification.created_at.isoformat(),
    }


@csrf_exempt
@require_http_methods(["POST"])
async def publish_notification(request: HttpRequest, group: str) -> JsonResponse:
    """POST /notifications/<group>/ — publish a notification to a group."""
    payload = json.loads(request.body or "{}")
    mediator = ChannelsNotificationMediator(get_channel_layer())
    repository = DjangoNotificationRepository()

    use_case = PublishNotificationUseCase(mediator, repository)
    notification = await use_case.execute(group, payload.get("message", {}))

    return JsonResponse(_notification_to_dict(notification), status=201)


@require_http_methods(["GET"])
def list_notifications(request: HttpRequest, group: str) -> JsonResponse:
    """GET /notifications/<group>/ — list every notification sent to a group."""
    repository = DjangoNotificationRepository()
    use_case = ListNotificationsUseCase(repository)
    notifications = use_case.execute(group)

    return JsonResponse([_notification_to_dict(n) for n in notifications], safe=False)
