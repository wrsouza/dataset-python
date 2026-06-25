"""URL patterns for the order_signals app."""

from __future__ import annotations

from django.urls import path

from order_signals.django_app.views import (
    create_order,
    order_audit_log,
    order_notification_log,
    update_order_status,
)

app_name = "order_signals"

urlpatterns = [
    path("orders/", create_order, name="create"),
    path("orders/<str:order_id>/status/", update_order_status, name="update-status"),
    path("orders/<str:order_id>/audit/", order_audit_log, name="audit-log"),
    path(
        "orders/<str:order_id>/notifications/",
        order_notification_log,
        name="notification-log",
    ),
]
