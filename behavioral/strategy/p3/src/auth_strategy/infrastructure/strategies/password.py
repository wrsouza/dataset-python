"""PasswordAuthStrategy — username + password, checked against a stored hash."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.hashers import check_password

from auth_strategy.django_app.models import UserCredentialModel
from auth_strategy.domain.entities import AuthResult
from auth_strategy.domain.interfaces import AuthenticationStrategy


class PasswordAuthStrategy(AuthenticationStrategy):
    def authenticate(self, credentials: dict[str, Any]) -> AuthResult:
        username = credentials.get("username", "")
        password = credentials.get("password", "")

        try:
            record = UserCredentialModel.objects.get(username=username)
        except UserCredentialModel.DoesNotExist:
            return AuthResult(
                success=False, strategy_name=self.get_name(), reason="user not found"
            )

        if not check_password(password, record.password_hash):
            return AuthResult(
                success=False, strategy_name=self.get_name(), reason="invalid password"
            )

        return AuthResult(
            success=True, strategy_name=self.get_name(), user_id=record.user_id
        )

    def get_name(self) -> str:
        return "password"
