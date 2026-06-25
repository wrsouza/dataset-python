"""WebSocket URL patterns for the realtime_notifications app."""

from __future__ import annotations

from django.urls import re_path

from realtime_notifications.infrastructure.consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path(r"^ws/notifications/(?P<group>\w+)/$", NotificationConsumer.as_asgi()),
]
