"""Domain entities for the Permission Decorator Layers project.

Plain dataclasses with no Django ORM dependency — the domain layer must
remain independent from the web framework and the database engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class AccessAction(StrEnum):
    """Action requested against a resource."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"


@dataclass(frozen=True)
class User:
    """A user attempting to access a resource."""

    user_id: str
    username: str
    roles: frozenset[str] = field(default_factory=frozenset)
    is_authenticated: bool = True

    def has_role(self, role: str) -> bool:
        """Return True when the user holds the given role."""
        return role in self.roles


ANONYMOUS_USER = User(user_id="", username="anonymous", is_authenticated=False)


@dataclass(frozen=True)
class Resource:
    """A protected domain resource (e.g. a document)."""

    resource_id: str
    owner_id: str
    title: str


@dataclass(frozen=True)
class RequestContext:
    """Everything a decorator layer needs to evaluate an access attempt."""

    user: User
    resource: Resource
    action: AccessAction
    required_role: str | None = None
    requested_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class ResourceAccessResult:
    """Outcome of an access attempt, built up as decorators are unwound."""

    granted: bool
    reason: str
    resource_id: str
    user_id: str
    layers_applied: tuple[str, ...] = field(default_factory=tuple)

    def with_layer(self, layer_name: str) -> ResourceAccessResult:
        """Return a copy recording that `layer_name` participated in the decision."""
        return ResourceAccessResult(
            granted=self.granted,
            reason=self.reason,
            resource_id=self.resource_id,
            user_id=self.user_id,
            layers_applied=(layer_name, *self.layers_applied),
        )

    def denied_by(self, layer_name: str, reason: str) -> ResourceAccessResult:
        """Return a denial recorded by `layer_name`, short-circuiting the chain."""
        return ResourceAccessResult(
            granted=False,
            reason=reason,
            resource_id=self.resource_id,
            user_id=self.user_id,
            layers_applied=(layer_name, *self.layers_applied),
        )


class AccessDeniedError(Exception):
    """Raised by use cases when an access attempt is rejected."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Access denied: {reason}")
