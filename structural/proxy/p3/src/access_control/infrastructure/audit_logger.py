"""Concrete AuditLogger backed by the Django ORM."""

from __future__ import annotations

from uuid import uuid4

from access_control.infrastructure.models import AuditLogModel


class DjangoAuditLogger:
    def log(
        self, user_id: str, action: str, resource_id: str, granted: bool, reason: str
    ) -> None:
        AuditLogModel.objects.create(
            log_id=str(uuid4()),
            user_id=user_id,
            action=action,
            resource_id=resource_id,
            granted=granted,
            reason=reason,
        )
