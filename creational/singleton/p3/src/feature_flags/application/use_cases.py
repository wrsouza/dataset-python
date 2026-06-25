"""Application use cases — orchestrate domain logic without knowing Django internals.

DIP: use cases depend on FeatureFlagManager via its public interface,
not on any concrete loader or Django request object.
SRP: each class has one job — check a flag, list all flags, or reload.
"""

from __future__ import annotations

from dataclasses import dataclass

from feature_flags.domain.entities import FlagConfig, FlagEvaluationResult, RegistryStats
from feature_flags.infrastructure.singleton import FeatureFlagManager


@dataclass
class CheckFlagRequest:
    """Input data for the CheckFlagUseCase."""

    flag_name: str
    user_id: str | None = None


class CheckFlagUseCase:
    """Evaluate a single feature flag for an optional user."""

    def __init__(self, manager: FeatureFlagManager) -> None:
        self._manager = manager

    def execute(self, request: CheckFlagRequest) -> FlagEvaluationResult:
        is_on = self._manager.is_enabled(request.flag_name, user_id=request.user_id)
        # Reconstruct a full result — is_enabled already did the evaluation.
        return FlagEvaluationResult(
            flag_name=request.flag_name,
            is_enabled=is_on,
            user_id=request.user_id,
            reason="evaluated",
        )


class ListAllFlagsUseCase:
    """Return all flag configurations as a dict snapshot."""

    def __init__(self, manager: FeatureFlagManager) -> None:
        self._manager = manager

    def execute(self) -> dict[str, FlagConfig]:
        return self._manager.get_all_flags()


class ReloadFlagsUseCase:
    """Reload flags from the source — triggered by POST /flags/reload."""

    def __init__(self, manager: FeatureFlagManager) -> None:
        self._manager = manager

    def execute(self) -> RegistryStats:
        self._manager.reload()
        return self._manager.get_stats()


class GetRegistryStatsUseCase:
    """Return runtime statistics for the flag registry singleton."""

    def __init__(self, manager: FeatureFlagManager) -> None:
        self._manager = manager

    def execute(self) -> RegistryStats:
        return self._manager.get_stats()
