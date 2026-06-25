"""Domain entities for infrastructure profile cloning.

`InfrastructureProfile` is the concrete prototype. It owns mutable nested
collections (tags, firewall rules, env vars) that MUST be deep-copied on
clone — sharing them with the original would let edits to a clone leak back
into the template it was cloned from, defeating the whole point of the
Prototype pattern.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field

from src.infra_profile.domain.interfaces import Prototype

DEFAULT_STORAGE_SIZE_GB = 20


@dataclass(slots=True)
class StorageConfig:
    """Disk/volume configuration attached to an infrastructure profile."""

    volume_type: str = "ssd"
    size_gb: int = DEFAULT_STORAGE_SIZE_GB
    encrypted: bool = True


@dataclass(slots=True)
class InfrastructureProfile(Prototype):
    """A reusable infrastructure definition that can be cloned and tuned.

    Represents something like a Terraform/CloudFormation "shape": instance
    type, region, tags, firewall rules, environment variables and storage.
    New profiles are typically created by cloning an existing template and
    overriding only the fields that differ (region, size, tags), rather than
    rebuilding the whole object from scratch.
    """

    name: str
    instance_type: str
    region: str
    tags: dict[str, str] = field(default_factory=dict)
    firewall_rules: list[str] = field(default_factory=list)
    env_vars: dict[str, str] = field(default_factory=dict)
    storage: StorageConfig = field(default_factory=StorageConfig)

    def clone(self) -> InfrastructureProfile:
        """Return an independent deep copy of this profile.

        Deep copy is essential here: `tags`, `firewall_rules`, `env_vars`
        and `storage` are mutable containers. A shallow copy would make the
        clone and the original share the same dict/list objects, so
        mutating the clone's tags would silently corrupt the template.
        """
        return copy.deepcopy(self)

    def __deepcopy__(self, memo: dict[int, object]) -> InfrastructureProfile:
        """Explicit deep-copy hook, kept for clarity and to avoid surprises.

        `copy.deepcopy` would already recurse correctly into the dataclass
        fields without this override, but defining it explicitly makes the
        cloning contract visible in the class itself — a student reading
        this file does not need to know `copy` module internals to see that
        every nested field is copied, not aliased.
        """
        cloned = InfrastructureProfile(
            name=self.name,
            instance_type=self.instance_type,
            region=self.region,
            tags=copy.deepcopy(self.tags, memo),
            firewall_rules=copy.deepcopy(self.firewall_rules, memo),
            env_vars=copy.deepcopy(self.env_vars, memo),
            storage=copy.deepcopy(self.storage, memo),
        )
        memo[id(self)] = cloned
        return cloned

    def apply_overrides(self, **overrides: object) -> None:
        """Mutate this instance in place with the given field overrides.

        Used right after cloning to adjust the few fields that differ from
        the template (e.g. region, instance_type) without touching the
        fields that should stay identical to the prototype.
        """
        for key, value in overrides.items():
            if not hasattr(self, key):
                message = f"Unknown InfrastructureProfile field: {key!r}"
                raise AttributeError(message)
            setattr(self, key, value)
