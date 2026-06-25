"""URL patterns for the workflow_approval_fsm app."""

from __future__ import annotations

from django.urls import path

from workflow_approval_fsm.django_app.views import (
    approve_request,
    create_request,
    get_request,
    reject_request,
    request_changes,
    submit_request,
)

app_name = "workflow_approval_fsm"

urlpatterns = [
    path("workflows/", create_request, name="create"),
    path("workflows/<str:request_id>/", get_request, name="get"),
    path("workflows/<str:request_id>/submit/", submit_request, name="submit"),
    path("workflows/<str:request_id>/approve/", approve_request, name="approve"),
    path("workflows/<str:request_id>/reject/", reject_request, name="reject"),
    path(
        "workflows/<str:request_id>/request-changes/",
        request_changes,
        name="request-changes",
    ),
]
