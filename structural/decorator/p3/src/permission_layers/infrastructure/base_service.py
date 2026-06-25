"""ConcreteComponent — the undecorated resource access service."""

from __future__ import annotations

from permission_layers.domain.entities import RequestContext, ResourceAccessResult
from permission_layers.domain.interfaces import ResourceAccessService
from permission_layers.infrastructure.repository import ResourceRepository

BASE_LAYER_NAME = "base_service"


class DocumentAccessService(ResourceAccessService):
    """ConcreteComponent — grants access whenever the resource exists.

    All authorization rules (authentication, roles, ownership) are added on
    top of this service by stacking decorators; this class only knows how
    to look the resource up.
    """

    def __init__(self, repository: ResourceRepository) -> None:
        self._repository = repository

    def access(self, context: RequestContext) -> ResourceAccessResult:
        resource = self._repository.find_by_id(context.resource.resource_id)
        if resource is None:
            return ResourceAccessResult(
                granted=False,
                reason=f"Resource '{context.resource.resource_id}' not found",
                resource_id=context.resource.resource_id,
                user_id=context.user.user_id,
            ).with_layer(BASE_LAYER_NAME)
        return ResourceAccessResult(
            granted=True,
            reason="Resource located; no authorization layer applied yet",
            resource_id=resource.resource_id,
            user_id=context.user.user_id,
        ).with_layer(BASE_LAYER_NAME)
