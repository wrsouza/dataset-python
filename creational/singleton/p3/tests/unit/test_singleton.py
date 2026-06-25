"""Unit tests for FeatureFlagManager Singleton.

Key assertions:
- Multiple calls return the SAME instance (identity check with `is`).
- Thread-safety: 50 concurrent threads get the same object.
- Flag evaluation: boolean, percentage, allowlist strategies.
- set_override() for test isolation.
"""

from __future__ import annotations

import threading
from typing import Any

import pytest

from feature_flags.domain.entities import FlagConfig, FlagType
from feature_flags.infrastructure.singleton import FeatureFlagManager, SingletonMeta


# ── Fake loader for tests ─────────────────────────────────────────────────────


class FakeFlagLoader:
    """In-memory loader — no file I/O in unit tests."""

    def __init__(self, flags: dict[str, FlagConfig] | None = None) -> None:
        self._flags = flags or {}

    def load(self) -> dict[str, FlagConfig]:
        return dict(self._flags)


def _make_boolean(name: str, enabled: bool = True) -> FlagConfig:
    return FlagConfig(name=name, enabled=enabled)


def _make_percentage(name: str, pct: int) -> FlagConfig:
    return FlagConfig(
        name=name,
        enabled=True,
        rollout_percentage=pct,
        flag_type=FlagType.PERCENTAGE,
    )


def _make_allowlist(name: str, users: list[str]) -> FlagConfig:
    return FlagConfig(
        name=name,
        enabled=True,
        allowlist=users,
        flag_type=FlagType.ALLOWLIST,
    )


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def reset_singleton() -> Any:
    """Clear the singleton registry before and after every test."""
    SingletonMeta._instances.pop(FeatureFlagManager, None)
    yield
    SingletonMeta._instances.pop(FeatureFlagManager, None)


@pytest.fixture()
def loader() -> FakeFlagLoader:
    return FakeFlagLoader(
        {
            "dark_mode": _make_boolean("dark_mode"),
            "disabled_flag": _make_boolean("disabled_flag", enabled=False),
            "new_checkout": _make_percentage("new_checkout", pct=50),
            "beta_search": _make_allowlist("beta_search", users=["user_1", "user_42"]),
        }
    )


@pytest.fixture()
def manager(loader: FakeFlagLoader) -> FeatureFlagManager:
    return FeatureFlagManager(loader=loader)


# ── Singleton identity tests ──────────────────────────────────────────────────


def test_same_instance_on_repeated_calls(loader: FakeFlagLoader) -> None:
    """Two successive calls to FeatureFlagManager() return the same object."""
    first = FeatureFlagManager(loader=loader)
    second = FeatureFlagManager(loader=loader)
    assert first is second, "Singleton violated: two distinct instances created"


def test_same_instance_three_references(loader: FakeFlagLoader) -> None:
    """id() is identical for all references to the singleton."""
    a = FeatureFlagManager(loader=loader)
    b = FeatureFlagManager(loader=loader)
    c = FeatureFlagManager(loader=loader)
    assert id(a) == id(b) == id(c)


def test_singleton_under_thread_contention(loader: FakeFlagLoader) -> None:
    """50 threads racing to obtain the singleton must all get the same object."""
    instances: list[FeatureFlagManager] = []
    lock = threading.Lock()

    def grab() -> None:
        instance = FeatureFlagManager(loader=loader)
        with lock:
            instances.append(instance)

    threads = [threading.Thread(target=grab) for _ in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(instances) == 50
    first = instances[0]
    assert all(inst is first for inst in instances), (
        "Thread-safety violated: multiple distinct FeatureFlagManager instances created"
    )


# ── Boolean flag evaluation ───────────────────────────────────────────────────


def test_boolean_enabled_flag(manager: FeatureFlagManager) -> None:
    assert manager.is_enabled("dark_mode") is True


def test_boolean_disabled_flag(manager: FeatureFlagManager) -> None:
    assert manager.is_enabled("disabled_flag") is False


def test_unknown_flag_returns_false(manager: FeatureFlagManager) -> None:
    """Unknown flags are fail-safe — return False instead of raising."""
    assert manager.is_enabled("nonexistent_flag") is False


# ── Percentage rollout evaluation ─────────────────────────────────────────────


def test_percentage_requires_user_id(manager: FeatureFlagManager) -> None:
    """Percentage flags without user_id return False (cannot bucket anonymous)."""
    assert manager.is_enabled("new_checkout", user_id=None) is False


def test_percentage_is_deterministic(manager: FeatureFlagManager) -> None:
    """Same user always lands in the same bucket — sticky rollout."""
    result1 = manager.is_enabled("new_checkout", user_id="user_abc")
    result2 = manager.is_enabled("new_checkout", user_id="user_abc")
    assert result1 == result2


def test_percentage_100_always_enabled(loader: FakeFlagLoader) -> None:
    """100% rollout — every user gets the feature."""
    loader._flags["full_rollout"] = _make_percentage("full_rollout", pct=100)
    mgr = FeatureFlagManager(loader=loader)
    for i in range(20):
        assert mgr.is_enabled("full_rollout", user_id=f"user_{i}") is True


def test_percentage_0_never_enabled(loader: FakeFlagLoader) -> None:
    """0% rollout — no user gets the feature."""
    loader._flags["no_rollout"] = _make_percentage("no_rollout", pct=0)
    mgr = FeatureFlagManager(loader=loader)
    for i in range(20):
        assert mgr.is_enabled("no_rollout", user_id=f"user_{i}") is False


# ── Allowlist evaluation ──────────────────────────────────────────────────────


def test_allowlist_member_gets_access(manager: FeatureFlagManager) -> None:
    assert manager.is_enabled("beta_search", user_id="user_1") is True


def test_allowlist_non_member_blocked(manager: FeatureFlagManager) -> None:
    assert manager.is_enabled("beta_search", user_id="user_99") is False


def test_allowlist_requires_user_id(manager: FeatureFlagManager) -> None:
    assert manager.is_enabled("beta_search", user_id=None) is False


# ── Override / test isolation ─────────────────────────────────────────────────


def test_set_override_forces_enabled(manager: FeatureFlagManager) -> None:
    manager.set_override("disabled_flag", True)
    assert manager.is_enabled("disabled_flag") is True


def test_set_override_forces_disabled(manager: FeatureFlagManager) -> None:
    manager.set_override("dark_mode", False)
    assert manager.is_enabled("dark_mode") is False


def test_clear_override_restores_original(manager: FeatureFlagManager) -> None:
    manager.set_override("dark_mode", False)
    manager.clear_override("dark_mode")
    assert manager.is_enabled("dark_mode") is True


# ── Reload ────────────────────────────────────────────────────────────────────


def test_reload_increments_counter(manager: FeatureFlagManager) -> None:
    stats_before = manager.get_stats()
    manager.reload()
    stats_after = manager.get_stats()
    assert stats_after.reload_count == stats_before.reload_count + 1


def test_reload_picks_up_new_flag(loader: FakeFlagLoader, manager: FeatureFlagManager) -> None:
    """reload() picks up flags added to the loader after initial load."""
    assert manager.is_enabled("new_feature") is False
    loader._flags["new_feature"] = _make_boolean("new_feature")
    manager.reload()
    assert manager.is_enabled("new_feature") is True


# ── get_all_flags ─────────────────────────────────────────────────────────────


def test_get_all_flags_returns_snapshot(manager: FeatureFlagManager) -> None:
    flags = manager.get_all_flags()
    assert "dark_mode" in flags
    assert "new_checkout" in flags
    assert "beta_search" in flags


# ── get_stats ─────────────────────────────────────────────────────────────────


def test_get_stats_counts_enabled_flags(manager: FeatureFlagManager) -> None:
    stats = manager.get_stats()
    assert stats.total_flags == 4
    # dark_mode, new_checkout, beta_search are enabled; disabled_flag is not
    assert stats.enabled_flags == 3


def test_get_stats_override_count(manager: FeatureFlagManager) -> None:
    manager.set_override("dark_mode", False)
    stats = manager.get_stats()
    assert stats.override_count == 1


# ── FlagConfig validation ────────────────────────────────────────────────────


def test_flag_config_rejects_invalid_percentage() -> None:
    with pytest.raises(ValueError, match="rollout_percentage"):
        FlagConfig(name="bad", enabled=True, rollout_percentage=150)


# ── Thread-safety: concurrent reads and writes ────────────────────────────────


def test_concurrent_is_enabled_calls(manager: FeatureFlagManager) -> None:
    """Many threads calling is_enabled concurrently must not raise."""
    errors: list[Exception] = []

    def check() -> None:
        try:
            for _ in range(100):
                manager.is_enabled("dark_mode", user_id="user_x")
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=check) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Concurrent read errors: {errors}"


def test_concurrent_reload_and_read(manager: FeatureFlagManager) -> None:
    """Interleaved reload() and is_enabled() calls must not corrupt state."""
    errors: list[Exception] = []

    def reload_loop() -> None:
        try:
            for _ in range(10):
                manager.reload()
        except Exception as exc:
            errors.append(exc)

    def read_loop() -> None:
        try:
            for _ in range(50):
                manager.is_enabled("dark_mode")
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=reload_loop) for _ in range(5)]
    threads += [threading.Thread(target=read_loop) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Concurrent reload/read errors: {errors}"
