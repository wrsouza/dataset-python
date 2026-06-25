"""OAuthStrategy — maps a (provider, provider_user_id) pair to a local user.

Simulates the final step of an OAuth flow: the provider has already
verified the user and handed back a `provider_user_id`; this strategy
only resolves that id to a local account.
"""

from __future__ import annotations

from typing import Any

from auth_strategy.django_app.models import OAuthIdentityModel
from auth_strategy.domain.entities import AuthResult
from auth_strategy.domain.interfaces import AuthenticationStrategy


class OAuthStrategy(AuthenticationStrategy):
    def authenticate(self, credentials: dict[str, Any]) -> AuthResult:
        provider = credentials.get("provider", "")
        provider_user_id = credentials.get("provider_user_id", "")

        try:
            record = OAuthIdentityModel.objects.get(
                provider=provider, provider_user_id=provider_user_id
            )
        except OAuthIdentityModel.DoesNotExist:
            return AuthResult(
                success=False,
                strategy_name=self.get_name(),
                reason="no linked account for this provider identity",
            )

        return AuthResult(
            success=True, strategy_name=self.get_name(), user_id=record.user_id
        )

    def get_name(self) -> str:
        return "oauth"
