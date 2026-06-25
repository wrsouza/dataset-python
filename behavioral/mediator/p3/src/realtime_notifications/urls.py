"""HTTP URL patterns for the realtime_notifications app."""

from __future__ import annotations

from django.urls import path

from realtime_notifications.views import list_notifications, publish_notification

app_name = "realtime_notifications"

urlpatterns = [
    path(
        "notifications/<str:group>/",
        publish_notification,
        name="notification-publish",
    ),
    path(
        "notifications/<str:group>/list/",
        list_notifications,
        name="notification-list",
    ),
]
