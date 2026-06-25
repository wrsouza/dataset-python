"""Use cases orchestrating the Prototype pattern for dashboard configs.

DIP: depends only on the DashboardRegistry abstraction (domain/interfaces.py),
never on JsonDashboardRegistry directly. The concrete registry is injected
by the composition root (app.py).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dashboard.domain.interfaces import DashboardConfig, DashboardRegistry


@dataclass
class CloneDashboardUseCase:
    """Clones a registered dashboard prototype and applies overrides.

    SRP: this use case only orchestrates cloning; persistence and
    rendering are handled elsewhere.
    """

    registry: DashboardRegistry

    def execute(self, template_name: str, overrides: dict[str, Any]) -> DashboardConfig:
        """Clone the named template applying the given overrides.

        Args:
            template_name: Name of a registered prototype.
            overrides: Field values to override on the clone.

        Returns:
            A brand-new DashboardConfig independent from the template.
        """
        return self.registry.clone(template_name, overrides)


@dataclass
class ListDashboardTemplatesUseCase:
    """Lists the names of all registered dashboard prototypes."""

    registry: DashboardRegistry

    def execute(self) -> list[str]:
        """Return all registered template names."""
        return self.registry.list_templates()


@dataclass
class GetDashboardTemplateUseCase:
    """Retrieves a registered dashboard prototype by name."""

    registry: DashboardRegistry

    def execute(self, template_name: str) -> DashboardConfig:
        """Return the registered template (the original, not a clone)."""
        return self.registry.get(template_name)


@dataclass
class RegisterDashboardTemplateUseCase:
    """Registers a new (or replacement) dashboard prototype."""

    registry: DashboardRegistry

    def execute(self, name: str, config: DashboardConfig) -> None:
        """Register `config` under `name` in the registry."""
        self.registry.register(name, config)


@dataclass
class EditClonedDashboardUseCase:
    """Edits fields of an already-cloned dashboard config.

    Demonstrates that edits to a clone never affect the original template:
    the clone is a fully independent object graph (deep copy).
    """

    def execute(
        self, cloned_config: DashboardConfig, edits: dict[str, Any]
    ) -> DashboardConfig:
        """Apply `edits` to `cloned_config` and return a new edited clone.

        Args:
            cloned_config: A config previously produced by clone().
            edits: Field values to override.

        Returns:
            A new DashboardConfig instance with edits applied.
        """
        return cloned_config.clone(edits)
