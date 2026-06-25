"""URL configuration for the Queue Bridge Django project."""

from __future__ import annotations

from django.urls import path

from task_queue.views.queue_views import dequeue_messages, enqueue_message, health_check

urlpatterns = [
    # GET /queue/health/<broker_type>/
    path("queue/health/<str:broker_type>/", health_check, name="queue-health"),
    # POST /queue/enqueue/<broker_type>/<client_type>/
    path(
        "queue/enqueue/<str:broker_type>/<str:client_type>/",
        enqueue_message,
        name="queue-enqueue",
    ),
    # GET /queue/dequeue/<broker_type>/<queue_name>/
    path(
        "queue/dequeue/<str:broker_type>/<str:queue_name>/",
        dequeue_messages,
        name="queue-dequeue",
    ),
]
