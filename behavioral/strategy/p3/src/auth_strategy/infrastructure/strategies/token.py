"""TokenAuthStrategy — a static bearer token identifies the user directly."""

from __future__ import annotations

from typing import Any

from auth_strategy.django_app.models import ApiTokenModel
from auth_strategy.domain.entities import AuthResult
from auth_strategy.domain.interfaces import AuthenticationStrategy


class TokenAuthStrategy(AuthenticationStrategy):
    def authenticate(self, credentials: dict[str, Any]) -> AuthResult:
        token = credentials.get("token", "")

        try:
            record = ApiTokenModel.objects.get(token=token)
        except ApiTokenModel.DoesNotExist:
            return AuthResult(
                success=False, strategy_name=self.get_name(), reason="invalid token"
            )

        if not record.is_active:
            return AuthResult(
                success=False, strategy_name=self.get_name(), reason="token revoked"
            )

        return AuthResult(
            success=True, strategy_name=self.get_name(), user_id=record.user_id
        )

    def get_name(self) -> str:
        return "token"
