"""Role-based authorization handler."""

from __future__ import annotations

from validation.domain.entities import APIRequest, APIResponse, UserRole
from validation.domain.interfaces import RequestHandler

# Endpoint → minimum required role mapping
_ENDPOINT_ROLES: dict[str, set[UserRole]] = {
    "/orders": {UserRole.USER, UserRole.MANAGER, UserRole.ADMIN},
    "/admin": {UserRole.ADMIN},
    "/public": {UserRole.GUEST, UserRole.USER, UserRole.MANAGER, UserRole.ADMIN},
}

_ROLE_HIERARCHY: list[UserRole] = [
    UserRole.GUEST,
    UserRole.USER,
    UserRole.MANAGER,
    UserRole.ADMIN,
]


def _has_sufficient_role(user_role: UserRole, allowed_roles: set[UserRole]) -> bool:
    """Return True if user_role meets or exceeds any allowed role."""
    user_level = _ROLE_HIERARCHY.index(user_role)
    return any(user_level >= _ROLE_HIERARCHY.index(r) for r in allowed_roles)


class RoleAuthorizationHandler(RequestHandler):
    """Checks that the authenticated user has the required role.

    SRP: only responsible for authorization (permission check).
    OCP: add new endpoints to _ENDPOINT_ROLES without modifying this class.
    """

    HANDLER_NAME = "RoleAuthorizationHandler"

    def handle(self, request: APIRequest) -> APIResponse | None:
        if request.user_role is None:
            return APIResponse.forbidden(
                message=(
                    "No role found on request — authentication must "
                    "precede authorization"
                ),
                handler_name=self.HANDLER_NAME,
            )

        allowed = _ENDPOINT_ROLES.get(request.endpoint, set())
        if not allowed:
            # Unknown endpoint: deny by default (fail-secure)
            return APIResponse.forbidden(
                message=f"No role configuration found for endpoint: {request.endpoint}",
                handler_name=self.HANDLER_NAME,
            )

        if not _has_sufficient_role(request.user_role, allowed):
            return APIResponse.forbidden(
                message=(
                    f"Role '{request.user_role.value}' is not authorized "
                    f"for {request.endpoint}"
                ),
                handler_name=self.HANDLER_NAME,
            )

        return self._pass_to_next(request)
