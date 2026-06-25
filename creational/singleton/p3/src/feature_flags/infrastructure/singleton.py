"""Singleton FeatureFlagManager via metaclass — thread-safe, reloadable.

Pattern: Singleton via Metaclass (same approach as P1/P2 for consistency).
Thread-safety: double-checked locking in SingletonMeta.__call__ +
               threading.RLock around flag reads/writes.

Why RLock instead of Lock?
  reload() calls _load_flags() which acquires the same lock — RLock allows
  the same thread to re-enter without deadlocking.
"""

from __future__ import annotations

import hashlib
import threading
from typing import Any, ClassVar

from feature_flags.domain.entities import (
    FlagConfig,
    FlagEvaluationResult,
    FlagType,
    RegistryStats,
)
from feature_flags.domain.interfaces import FlagLoader


class SingletonMeta(type):
    """Metaclass enforcing one instance per class with double-checked locking."""

    _instances: ClassVar[dict[type, Any]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class FeatureFlagManager(metaclass=SingletonMeta):
    """Global feature flag registry loaded once and shared across all Django views.

    SRP: this class is solely responsible for flag evaluation and lifecycle.
    It does not know about HTTP, Django models, or persistence format.

    OCP: evaluation strategies are determined by FlagType enum — adding a new
    strategy only requires a new FlagType value + one private method, without
    modifying existing evaluation paths.

    Usage:
        manager = FeatureFlagManager(loader=JsonFlagLoader("flags.json"))
        manager.is_enabled("dark_mode")
        manager.is_enabled("new_checkout", user_id="user_42")
    """

    def __init__(self, loader: FlagLoader) -> None:
        # Guard: SingletonMeta guarantees __init__ runs once, but we still
        # protect _initialized to be explicit about the contract.
        if getattr(self, "_initialized", False):
            return
        self._loader = loader
        self._flags: dict[str, FlagConfig] = {}
        self._overrides: dict[str, bool] = {}
        self._rlock = threading.RLock()
        self._reload_count: int = 0
        self._initialized = True
        self._load_flags()

    # ── Public API ────────────────────────────────────────────────────────────

    def is_enabled(self, flag: str, user_id: str | None = None) -> bool:
        """Evaluate a flag for the given user.

        Returns False for unknown flags — fail-safe default.
        """
        result = self._evaluate(flag, user_id)
        return result.is_enabled

    def get_all_flags(self) -> dict[str, FlagConfig]:
        """Return a snapshot of all loaded flag configurations."""
        with self._rlock:
            return dict(self._flags)

    def reload(self) -> None:
        """Reload flags from the source (e.g. after a JSON file update).

        Overrides set via set_override() are preserved across reloads
        because they are kept in a separate dict.
        """
        with self._rlock:
            self._load_flags()

    def set_override(self, flag: str, value: bool) -> None:
        """Pin a flag to a fixed value — intended for tests only.

        Overrides bypass all evaluation logic and always return `value`.
        Clear with clear_override(flag) when the test is done.
        """
        with self._rlock:
            self._overrides[flag] = value

    def clear_override(self, flag: str) -> None:
        """Remove a test override for the given flag."""
        with self._rlock:
            self._overrides.pop(flag, None)

    def get_stats(self) -> RegistryStats:
        """Return runtime statistics without exposing internal state directly."""
        with self._rlock:
            return RegistryStats(
                total_flags=len(self._flags),
                enabled_flags=sum(1 for f in self._flags.values() if f.enabled),
                reload_count=self._reload_count,
                override_count=len(self._overrides),
            )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _load_flags(self) -> None:
        """Delegate loading to the injected FlagLoader and increment counter."""
        self._flags = self._loader.load()
        self._reload_count += 1

    def _evaluate(self, flag: str, user_id: str | None) -> FlagEvaluationResult:
        """Dispatch evaluation to the correct strategy based on flag type."""
        with self._rlock:
            # Test overrides take absolute precedence.
            if flag in self._overrides:
                return FlagEvaluationResult(
                    flag_name=flag,
                    is_enabled=self._overrides[flag],
                    user_id=user_id,
                    reason="override",
                )

            config = self._flags.get(flag)
            if config is None:
                return FlagEvaluationResult(
                    flag_name=flag,
                    is_enabled=False,
                    user_id=user_id,
                    reason="unknown_flag",
                )

            if not config.enabled:
                return FlagEvaluationResult(
                    flag_name=flag,
                    is_enabled=False,
                    user_id=user_id,
                    reason="flag_disabled",
                )

            return self._evaluate_by_type(config, user_id)

    def _evaluate_by_type(
        self, config: FlagConfig, user_id: str | None
    ) -> FlagEvaluationResult:
        """Route to the correct evaluation strategy — OCP extension point."""
        if config.flag_type == FlagType.BOOLEAN:
            return self._evaluate_boolean(config, user_id)
        if config.flag_type == FlagType.PERCENTAGE:
            return self._evaluate_percentage(config, user_id)
        if config.flag_type == FlagType.ALLOWLIST:
            return self._evaluate_allowlist(config, user_id)
        # Unreachable with current enum, but guards against future additions.
        return FlagEvaluationResult(
            flag_name=config.name,
            is_enabled=False,
            user_id=user_id,
            reason="unknown_flag_type",
        )

    def _evaluate_boolean(
        self, config: FlagConfig, user_id: str | None
    ) -> FlagEvaluationResult:
        return FlagEvaluationResult(
            flag_name=config.name,
            is_enabled=True,
            user_id=user_id,
            reason="boolean_enabled",
        )

    def _evaluate_percentage(
        self, config: FlagConfig, user_id: str | None
    ) -> FlagEvaluationResult:
        """Hash user_id into a deterministic 0-99 bucket.

        Using SHA-256 ensures uniform distribution; the same user always
        lands in the same bucket (sticky rollout).
        """
        if user_id is None:
            return FlagEvaluationResult(
                flag_name=config.name,
                is_enabled=False,
                user_id=user_id,
                reason="percentage_requires_user_id",
            )
        digest = hashlib.sha256(f"{config.name}:{user_id}".encode()).hexdigest()
        bucket = int(digest[:8], 16) % 100
        enabled = bucket < config.rollout_percentage
        return FlagEvaluationResult(
            flag_name=config.name,
            is_enabled=enabled,
            user_id=user_id,
            reason=f"percentage_bucket_{bucket}",
        )

    def _evaluate_allowlist(
        self, config: FlagConfig, user_id: str | None
    ) -> FlagEvaluationResult:
        if user_id is None:
            return FlagEvaluationResult(
                flag_name=config.name,
                is_enabled=False,
                user_id=user_id,
                reason="allowlist_requires_user_id",
            )
        enabled = user_id in config.allowlist
        return FlagEvaluationResult(
            flag_name=config.name,
            is_enabled=enabled,
            user_id=user_id,
            reason="allowlist_match" if enabled else "allowlist_no_match",
        )
