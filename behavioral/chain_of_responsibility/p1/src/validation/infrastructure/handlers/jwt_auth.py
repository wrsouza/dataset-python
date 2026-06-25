"""JWT authentication handler."""

from __future__ import annotations

import base64
import json

from validation.domain.entities import APIRequest, APIResponse, UserRole
from validation.domain.interfaces import RequestHandler

# Simulated secret — in production use env var + cryptographic library
_FAKE_SECRET = "supersecret"  # noqa: S105 (demo placeholder, not a real credential)


def _decode_fake_jwt(token: str) -> dict[str, object] | None:
    """Decode a simplified base64 JWT for demo purposes.

    Real projects use python-jose or PyJWT with RS256.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:  # noqa: PLR2004
            return None
        payload_bytes = base64.urlsafe_b64decode(parts[1] + "==")
        return json.loads(payload_bytes)  # type: ignore[no-any-return]
    except Exception:  # noqa: BLE001
        return None


class JWTAuthHandler(RequestHandler):
    """Validates the Authorization Bearer token.

    SRP: only responsible for authentication (identity verification).
    """

    HANDLER_NAME = "JWTAuthHandler"
    _BEARER_PREFIX = "Bearer "

    def handle(self, request: APIRequest) -> APIResponse | None:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith(self._BEARER_PREFIX):
            return APIResponse.unauthorized(
                message="Missing or malformed Authorization header",
                handler_name=self.HANDLER_NAME,
            )

        token = auth_header[len(self._BEARER_PREFIX) :]
        payload = _decode_fake_jwt(token)
        if payload is None:
            return APIResponse.unauthorized(
                message="Invalid JWT token",
                handler_name=self.HANDLER_NAME,
            )

        # Enrich request with identity from token for downstream handlers
        request.user_id = str(payload.get("sub", ""))
        role_value = str(payload.get("role", "guest"))
        try:
            request.user_role = UserRole(role_value)
        except ValueError:
            request.user_role = UserRole.GUEST

        return self._pass_to_next(request)
