"""Django AppConfig for the workflow_approval_fsm app."""

from __future__ import annotations

from django.apps import AppConfig


class WorkflowApprovalFsmConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "workflow_approval_fsm.django_app"
    label = "workflow_approval_fsm_django_app"
