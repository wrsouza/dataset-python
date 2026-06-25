"""Domain interfaces for the Permission Decorator Layers project.

Defines the Component ABC (`ResourceAccessService`) at the heart of the GoF
Decorator pattern. Both the concrete base service and every permission
decorator implement this single, narrow interface (Interface Segregation),
so any composition of layers can stand in for the plain service
(Liskov Substitution) without the caller knowing which layers are stacked
(Open/Closed — new layers are added as new subclasses, not by editing
existing code).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from permission_layers.domain.entities import RequestContext, ResourceAccessResult


class ResourceAccessService(ABC):
    """Component — the single contract shared by the base service and all decorators."""

    @abstractmethod
    def access(self, context: RequestContext) -> ResourceAccessResult:
        """Evaluate (or perform) the access attempt described by `context`."""
        ...


class ResourceAccessDecorator(ResourceAccessService):
    """Decorator — wraps a `ResourceAccessService` and delegates to it by default.

    Concrete decorators override `access` to add a permission check or a
    side effect (logging) before/after calling `self._wrapped.access(context)`.
    Decorators never need to know the concrete type wrapped — they depend
    only on the abstraction (Dependency Inversion).
    """

    def __init__(self, wrapped: ResourceAccessService) -> None:
        self._wrapped = wrapped

    def access(self, context: RequestContext) -> ResourceAccessResult:
        """Default delegation — subclasses inject behaviour around this call."""
        return self._wrapped.access(context)
