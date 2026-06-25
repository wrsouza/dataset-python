"""Prototype registry: a catalog of pre-configured infrastructure templates.

This is the classic "Prototype Registry" variant of the pattern: instead of
clients constructing prototypes themselves, they ask the registry for a
named template and clone it. Adding a new template only requires calling
`register()` — no existing code (including this class) needs to change,
which is the Open/Closed Principle in action.
"""

from __future__ import annotations

from src.infra_profile.domain.entities import InfrastructureProfile, StorageConfig

PROD_API_TEMPLATE = "prod-api-template"
STAGING_DB_TEMPLATE = "staging-db-template"


class TemplateNotFoundError(KeyError):
    """Raised when a requested prototype template does not exist."""


class ProfileRegistry:
    """Holds named `InfrastructureProfile` prototypes available for cloning.

    New resource templates are added via `register()`, which accepts any
    `InfrastructureProfile` instance. There is no `if/elif` chain keyed on
    template type to maintain — extending the catalog never requires
    modifying this class (Open/Closed Principle).
    """

    def __init__(self) -> None:
        self._templates: dict[str, InfrastructureProfile] = {}

    def register(self, profile: InfrastructureProfile) -> None:
        """Add (or replace) a prototype template under its own `name`."""
        self._templates[profile.name] = profile

    def get_template(self, name: str) -> InfrastructureProfile:
        """Return the prototype registered under `name`.

        Raises:
            TemplateNotFoundError: if no template is registered with that name.
        """
        template = self._templates.get(name)
        if template is None:
            message = f"No template registered under name {name!r}"
            raise TemplateNotFoundError(message)
        return template

    def list_template_names(self) -> list[str]:
        """Return the names of every registered template, sorted alphabetically."""
        return sorted(self._templates)


def build_default_registry() -> ProfileRegistry:
    """Create a `ProfileRegistry` pre-loaded with two realistic templates."""
    registry = ProfileRegistry()
    registry.register(
        InfrastructureProfile(
            name=PROD_API_TEMPLATE,
            instance_type="m5.xlarge",
            region="us-east-1",
            tags={"environment": "production", "team": "platform"},
            firewall_rules=["allow-443-from-alb", "deny-all-default"],
            env_vars={"LOG_LEVEL": "INFO", "TIMEOUT_SECONDS": "30"},
            storage=StorageConfig(volume_type="ssd", size_gb=100, encrypted=True),
        )
    )
    registry.register(
        InfrastructureProfile(
            name=STAGING_DB_TEMPLATE,
            instance_type="db.t3.medium",
            region="us-east-1",
            tags={"environment": "staging", "team": "data"},
            firewall_rules=["allow-5432-from-vpc"],
            env_vars={"LOG_LEVEL": "DEBUG"},
            storage=StorageConfig(volume_type="gp3", size_gb=50, encrypted=True),
        )
    )
    return registry
