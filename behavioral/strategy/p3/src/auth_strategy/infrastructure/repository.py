"""Django ORM repository for the authentication attempt log."""

from __future__ import annotations

from datetime import UTC, datetime

from auth_strategy.django_app.models import AuthAttemptLogModel
from auth_strategy.domain.entities import AuthResult


class DjangoAuthAttemptLogRepository:
    def append(self, result: AuthResult) -> None:
        AuthAttemptLogModel.objects.create(
            strategy_name=result.strategy_name,
            success=result.success,
            user_id=result.user_id,
            reason=result.reason,
            created_at=datetime.now(UTC),
        )

    def list_all(self) -> list[AuthResult]:
        rows = AuthAttemptLogModel.objects.all()
        return [
            AuthResult(
                success=row.success,
                strategy_name=row.strategy_name,
                user_id=row.user_id,
                reason=row.reason,
            )
            for row in rows
        ]
