"""Domain entities for feature flags.

These dataclasses are pure data — no framework coupling, no I/O.
SRP: each class has exactly one reason to change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class FlagType(str, Enum):
    """Discriminates the evaluation strategy for a feature flag."""

    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    ALLOWLIST = "allowlist"


@dataclass(frozen=True)
class FlagConfig:
    """Immutable snapshot of a single flag's configuration.

    Fields:
        name:               Unique flag identifier.
        enabled:            Master switch — False short-circuits all evaluations.
        rollout_percentage: 0-100; used only when type is PERCENTAGE.
        allowlist:          User IDs explicitly granted access.
        flag_type:          Determines the evaluation strategy.
    """

    name: str
    enabled: bool
    rollout_percentage: int = 0
    allowlist: list[str] = field(default_factory=list)
    flag_type: FlagType = FlagType.BOOLEAN

    def __post_init__(self) -> None:
        if not 0 <= self.rollout_percentage <= 100:
            raise ValueError(
                f"rollout_percentage must be 0-100, got {self.rollout_percentage}"
            )


@dataclass(frozen=True)
class FlagEvaluationResult:
    """Result of evaluating a flag for a specific user.

    Carries enough context for audit logging without re-querying.
    """

    flag_name: str
    is_enabled: bool
    user_id: str | None
    reason: str


@dataclass
class RegistryStats:
    """Runtime statistics for the FeatureFlagManager singleton."""

    total_flags: int
    enabled_flags: int
    reload_count: int
    override_count: int
