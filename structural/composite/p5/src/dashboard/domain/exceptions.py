"""Domain-specific exceptions for the dashboard component tree."""

from __future__ import annotations


class DashboardComponentError(Exception):
    """Base class for all dashboard-component domain errors."""


class DuplicateChildComponentError(DashboardComponentError):
    """Raised when a container gets a child whose name already exists."""

    def __init__(self, container_name: str, child_name: str) -> None:
        self.container_name = container_name
        self.child_name = child_name
        super().__init__(
            f"Container '{container_name}' already has a child named " f"'{child_name}'"
        )


class UnknownComponentTypeError(DashboardComponentError):
    """Raised when a definition references an unregistered component type."""

    def __init__(self, component_type: str) -> None:
        self.component_type = component_type
        super().__init__(f"Unknown component type '{component_type}'")


class DashboardDefinitionError(DashboardComponentError):
    """Raised when a dashboard definition (dict/JSON) cannot be parsed."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid dashboard definition: {reason}")
