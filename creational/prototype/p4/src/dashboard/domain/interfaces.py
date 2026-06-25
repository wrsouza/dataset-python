"""Domain interfaces for the Dashboard Config Prototype pattern."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DashboardConfig(ABC):
    """Prototype interface for dashboard configurations.

    Concrete dashboard configs (sales, inventory, marketing) must implement
    clone() to allow creating variant copies without knowing the concrete class.
    OCP: new dashboard types extend this without modifying existing code.
    """

    @abstractmethod
    def clone(self, overrides: dict[str, Any]) -> DashboardConfig:
        """Create an independent copy with overrides applied.

        Args:
            overrides: Fields to override in the cloned config.

        Returns:
            A new DashboardConfig instance independent from this one.
        """
        ...

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dictionary."""
        ...

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> DashboardConfig:
        """Deserialize from a dictionary (inverse of to_dict)."""
        ...

    @property
    @abstractmethod
    def title(self) -> str:
        """Dashboard title."""
        ...

    @property
    @abstractmethod
    def dashboard_type(self) -> str:
        """Concrete type identifier (sales / inventory / marketing)."""
        ...


class DashboardRegistry(ABC):
    """Registry interface for managing dashboard config prototypes.

    Follows OCP: new dashboard types are registered without modifying this.
    SRP: only responsible for storing, loading and cloning configs.
    """

    @abstractmethod
    def register(self, name: str, config: DashboardConfig) -> None:
        """Register a config template under the given name."""
        ...

    @abstractmethod
    def get(self, name: str) -> DashboardConfig:
        """Retrieve a registered config template by name."""
        ...

    @abstractmethod
    def clone(self, name: str, overrides: dict[str, Any]) -> DashboardConfig:
        """Clone a registered config and apply overrides."""
        ...

    @abstractmethod
    def list_templates(self) -> list[str]:
        """Return all registered template names."""
        ...
