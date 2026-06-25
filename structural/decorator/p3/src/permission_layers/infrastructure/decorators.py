"""Concrete permission decorators — the stackable authorization layers.

Each decorator implements a single rule (Single Responsibility) and can be
composed with any other decorator in any order around any
`ResourceAccessService` (Open/Closed + Liskov Substitution):

    AuditLogDecorator(
        RequireOwnershipDecorator(
            RequireRoleDecorator(
                RequireAuthDecorator(base_service),
                required_role="editor",
            )
        )
    )
"""

from __future__ import annotations

import logging

from permission_layers.domain.entities import RequestContext, ResourceAccessResult
from permission_layers.domain.interfaces import ResourceAccessDecorator

logger = logging.getLogger("permission_layers.audit")


class RequireAuthDecorator(ResourceAccessDecorator):
    """Denies access unless the request's user is authenticated."""

    LAYER_NAME = "require_auth"

    def access(self, context: RequestContext) -> ResourceAccessResult:
        if not context.user.is_authenticated:
            return ResourceAccessResult(
                granted=False,
                reason="User is not authenticated",
                resource_id=context.resource.resource_id,
                user_id=context.user.user_id,
            ).with_layer(self.LAYER_NAME)
        return self._wrapped.access(context).with_layer(self.LAYER_NAME)


class RequireRoleDecorator(ResourceAccessDecorator):
    """Denies access unless the user holds `required_role`."""

    LAYER_NAME = "require_role"

    def __init__(self, wrapped: ResourceAccessDecorator, required_role: str) -> None:
        super().__init__(wrapped)
        self._required_role = required_role

    def access(self, context: RequestContext) -> ResourceAccessResult:
        inner_result = self._wrapped.access(context)
        if not inner_result.granted:
            return inner_result.with_layer(self.LAYER_NAME)
        if not context.user.has_role(self._required_role):
            return inner_result.denied_by(
                self.LAYER_NAME,
                f"User lacks required role '{self._required_role}'",
            )
        return inner_result.with_layer(self.LAYER_NAME)


class RequireOwnershipDecorator(ResourceAccessDecorator):
    """Denies access unless the user owns the target resource."""

    LAYER_NAME = "require_ownership"

    def access(self, context: RequestContext) -> ResourceAccessResult:
        inner_result = self._wrapped.access(context)
        if not inner_result.granted:
            return inner_result.with_layer(self.LAYER_NAME)
        if context.resource.owner_id != context.user.user_id:
            return inner_result.denied_by(
                self.LAYER_NAME,
                f"User '{context.user.user_id}' does not own resource "
                f"'{context.resource.resource_id}'",
            )
        return inner_result.with_layer(self.LAYER_NAME)


class AuditLogDecorator(ResourceAccessDecorator):
    """Logs every access attempt, regardless of the final decision.

    Typically placed as the outermost layer so it observes the final,
    fully-evaluated result without influencing the authorization outcome.
    """

    LAYER_NAME = "audit_log"

    def access(self, context: RequestContext) -> ResourceAccessResult:
        result = self._wrapped.access(context)
        outcome = "GRANTED" if result.granted else "DENIED"
        logger.info(
            "AUDIT action=%s user=%s resource=%s outcome=%s reason=%s",
            context.action.value,
            context.user.user_id or "<anonymous>",
            context.resource.resource_id,
            outcome,
            result.reason,
        )
        return result.with_layer(self.LAYER_NAME)
