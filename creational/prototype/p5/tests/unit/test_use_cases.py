"""Unit tests for application use cases, using fake/in-memory repositories."""

from __future__ import annotations

import pytest

from src.infra_profile.application.use_cases import (
    CloneProfileUseCase,
    CreateProfileUseCase,
    ListSavedProfilesUseCase,
    ListTemplatesUseCase,
    ProfileAlreadyExistsError,
    SaveProfileUseCase,
    ShowProfileUseCase,
)
from src.infra_profile.domain.entities import InfrastructureProfile
from src.infra_profile.domain.interfaces import ProfileRepository
from src.infra_profile.infrastructure.registry import ProfileRegistry


class FakeProfileRepository:
    """In-memory stand-in for ProfileRepository, used to isolate use cases
    from any real persistence mechanism (Dependency Inversion in action)."""

    def __init__(self) -> None:
        self._store: dict[str, InfrastructureProfile] = {}

    def save(self, profile: InfrastructureProfile) -> None:
        self._store[profile.name] = profile

    def get(self, name: str) -> InfrastructureProfile | None:
        return self._store.get(name)

    def list_all(self) -> list[InfrastructureProfile]:
        return sorted(self._store.values(), key=lambda profile: profile.name)


def _as_repository(fake: FakeProfileRepository) -> ProfileRepository:
    return fake


def test_clone_profile_use_case_applies_overrides(
    registry: ProfileRegistry, sample_profile: InfrastructureProfile
) -> None:
    use_case = CloneProfileUseCase(registry=registry)

    cloned = use_case.execute(
        sample_profile.name, "staging-api-template", region="us-west-2"
    )

    assert cloned.name == "staging-api-template"
    assert cloned.region == "us-west-2"
    assert sample_profile.region == "us-east-1"


def test_clone_profile_use_case_does_not_mutate_template_tags(
    registry: ProfileRegistry, sample_profile: InfrastructureProfile
) -> None:
    use_case = CloneProfileUseCase(registry=registry)

    cloned = use_case.execute(sample_profile.name, "copy")
    cloned.tags["new"] = "value"

    assert "new" not in sample_profile.tags


def test_list_templates_use_case_returns_registered_names(
    registry: ProfileRegistry,
) -> None:
    use_case = ListTemplatesUseCase(registry=registry)

    assert use_case.execute() == ["prod-api-template"]


def test_create_profile_use_case_persists_new_profile() -> None:
    fake = FakeProfileRepository()
    use_case = CreateProfileUseCase(repository=_as_repository(fake))

    created = use_case.execute(
        name="dev-box", instance_type="t3.micro", region="us-east-1"
    )

    assert fake.get("dev-box") == created


def test_create_profile_use_case_rejects_duplicate_name() -> None:
    fake = FakeProfileRepository()
    use_case = CreateProfileUseCase(repository=_as_repository(fake))
    use_case.execute(name="dev-box", instance_type="t3.micro", region="us-east-1")

    with pytest.raises(ProfileAlreadyExistsError):
        use_case.execute(name="dev-box", instance_type="t3.micro", region="us-east-1")


def test_save_profile_use_case_delegates_to_repository(
    sample_profile: InfrastructureProfile,
) -> None:
    fake = FakeProfileRepository()
    use_case = SaveProfileUseCase(repository=_as_repository(fake))

    use_case.execute(sample_profile)

    assert fake.get(sample_profile.name) == sample_profile


def test_show_profile_use_case_returns_none_when_missing() -> None:
    fake = FakeProfileRepository()
    use_case = ShowProfileUseCase(repository=_as_repository(fake))

    assert use_case.execute("nope") is None


def test_list_saved_profiles_use_case_returns_all(
    sample_profile: InfrastructureProfile,
) -> None:
    fake = FakeProfileRepository()
    fake.save(sample_profile)
    use_case = ListSavedProfilesUseCase(repository=_as_repository(fake))

    assert use_case.execute() == [sample_profile]
