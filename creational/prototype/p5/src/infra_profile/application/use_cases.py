"""Use cases orchestrating the Prototype pattern for infrastructure profiles.

Every use case receives its `ProfileRepository` dependency through the
constructor (Dependency Injection) and depends only on the `ProfileRepository`
Protocol from the domain layer — never on `JsonProfileRepository` directly.
This is the Dependency Inversion Principle: swapping storage technology
later requires no change here.
"""

from __future__ import annotations

from src.infra_profile.domain.entities import InfrastructureProfile, StorageConfig
from src.infra_profile.domain.interfaces import ProfileRepository
from src.infra_profile.infrastructure.registry import ProfileRegistry


class ProfileAlreadyExistsError(ValueError):
    """Raised when creating a profile whose name is already persisted."""


class CloneProfileUseCase:
    """Clone a registered template and apply field overrides to the copy."""

    def __init__(self, registry: ProfileRegistry) -> None:
        self._registry = registry

    def execute(
        self, template_name: str, new_name: str, **overrides: object
    ) -> InfrastructureProfile:
        """Return a deep clone of `template_name`, renamed and overridden.

        The clone never mutates the template stored in the registry: the
        Prototype's `clone()` deep-copies all nested state before any
        override is applied.
        """
        template = self._registry.get_template(template_name)
        cloned = template.clone()
        if not isinstance(cloned, InfrastructureProfile):  # pragma: no cover
            message = "Cloned object is not an InfrastructureProfile"
            raise TypeError(message)
        cloned.apply_overrides(name=new_name, **overrides)
        return cloned


class ListTemplatesUseCase:
    """List the names of every prototype template available for cloning."""

    def __init__(self, registry: ProfileRegistry) -> None:
        self._registry = registry

    def execute(self) -> list[str]:
        """Return the sorted list of registered template names."""
        return self._registry.list_template_names()


class CreateProfileUseCase:
    """Build a brand-new `InfrastructureProfile` from scratch (no cloning)."""

    def __init__(self, repository: ProfileRepository) -> None:
        self._repository = repository

    def execute(
        self,
        name: str,
        instance_type: str,
        region: str,
        storage: StorageConfig | None = None,
    ) -> InfrastructureProfile:
        """Create and persist a fresh profile, rejecting duplicate names."""
        if self._repository.get(name) is not None:
            message = f"Profile {name!r} already exists"
            raise ProfileAlreadyExistsError(message)
        profile = InfrastructureProfile(
            name=name,
            instance_type=instance_type,
            region=region,
            storage=storage or StorageConfig(),
        )
        self._repository.save(profile)
        return profile


class SaveProfileUseCase:
    """Persist a (typically just-cloned) profile to the repository."""

    def __init__(self, repository: ProfileRepository) -> None:
        self._repository = repository

    def execute(self, profile: InfrastructureProfile) -> None:
        """Save `profile`, overwriting any existing entry with the same name."""
        self._repository.save(profile)


class ShowProfileUseCase:
    """Fetch a single persisted profile by name."""

    def __init__(self, repository: ProfileRepository) -> None:
        self._repository = repository

    def execute(self, name: str) -> InfrastructureProfile | None:
        """Return the profile stored under `name`, or None if not found."""
        return self._repository.get(name)


class ListSavedProfilesUseCase:
    """List every profile persisted in the repository."""

    def __init__(self, repository: ProfileRepository) -> None:
        self._repository = repository

    def execute(self) -> list[InfrastructureProfile]:
        """Return all persisted profiles."""
        return self._repository.list_all()
