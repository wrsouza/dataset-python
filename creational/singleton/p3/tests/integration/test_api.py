"""Integration tests for Django feature flag API endpoints.

Uses Django's test client — no real HTTP server needed.
The FeatureFlagManager singleton is reset between tests via the fixture.
"""

from __future__ import annotations

import json
import os
from typing import Any

import pytest

# Configure Django settings before importing anything Django-related.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import django
from django.test import Client, RequestFactory

# Bootstrap Django before fixtures/tests run.
django.setup()

from feature_flags.domain.entities import FlagConfig, FlagType
from feature_flags.infrastructure.singleton import FeatureFlagManager, SingletonMeta


class FakeFlagLoader:
    def __init__(self) -> None:
        self._flags: dict[str, FlagConfig] = {
            "dark_mode": FlagConfig(name="dark_mode", enabled=True),
            "disabled_flag": FlagConfig(name="disabled_flag", enabled=False),
            "experimental_dashboard": FlagConfig(
                name="experimental_dashboard", enabled=True
            ),
            "beta_search": FlagConfig(
                name="beta_search",
                enabled=True,
                allowlist=["user_1"],
                flag_type=FlagType.ALLOWLIST,
            ),
        }

    def load(self) -> dict[str, FlagConfig]:
        return dict(self._flags)


@pytest.fixture(autouse=True)
def reset_and_init_singleton() -> Any:
    """Ensure a fresh singleton with FakeFlagLoader for every test."""
    SingletonMeta._instances.pop(FeatureFlagManager, None)
    FeatureFlagManager(loader=FakeFlagLoader())
    yield
    SingletonMeta._instances.pop(FeatureFlagManager, None)


@pytest.fixture()
def client() -> Client:
    return Client()


# ── GET /flags/ ───────────────────────────────────────────────────────────────


def test_list_flags_returns_200(client: Client) -> None:
    response = client.get("/flags/")
    assert response.status_code == 200


def test_list_flags_contains_expected_keys(client: Client) -> None:
    data = json.loads(client.get("/flags/").content)
    assert "flags" in data
    assert "stats" in data
    assert "singleton_id" in data


def test_list_flags_shows_dark_mode(client: Client) -> None:
    data = json.loads(client.get("/flags/").content)
    assert "dark_mode" in data["flags"]
    assert data["flags"]["dark_mode"]["enabled"] is True


def test_list_flags_same_singleton_id_on_repeated_calls(client: Client) -> None:
    """The singleton_id must be identical across requests."""
    id1 = json.loads(client.get("/flags/").content)["singleton_id"]
    id2 = json.loads(client.get("/flags/").content)["singleton_id"]
    assert id1 == id2, "Different requests returned different singleton instances"


# ── POST /flags/reload ────────────────────────────────────────────────────────


def test_reload_returns_200(client: Client) -> None:
    response = client.post("/flags/reload")
    assert response.status_code == 200


def test_reload_increments_reload_count(client: Client) -> None:
    before = json.loads(client.get("/flags/").content)["stats"]["reload_count"]
    client.post("/flags/reload")
    after = json.loads(client.get("/flags/").content)["stats"]["reload_count"]
    assert after == before + 1


def test_reload_with_get_returns_405(client: Client) -> None:
    response = client.get("/flags/reload")
    assert response.status_code == 405


# ── GET /flags/<name>/check ───────────────────────────────────────────────────


def test_check_enabled_flag(client: Client) -> None:
    data = json.loads(client.get("/flags/dark_mode/check").content)
    assert data["is_enabled"] is True
    assert data["flag"] == "dark_mode"


def test_check_disabled_flag(client: Client) -> None:
    data = json.loads(client.get("/flags/disabled_flag/check").content)
    assert data["is_enabled"] is False


def test_check_unknown_flag_returns_false(client: Client) -> None:
    data = json.loads(client.get("/flags/nonexistent/check").content)
    assert data["is_enabled"] is False


def test_check_allowlist_with_allowed_user(client: Client) -> None:
    data = json.loads(
        client.get("/flags/beta_search/check?user_id=user_1").content
    )
    assert data["is_enabled"] is True
    assert data["user_id"] == "user_1"


def test_check_allowlist_with_blocked_user(client: Client) -> None:
    data = json.loads(
        client.get("/flags/beta_search/check?user_id=user_99").content
    )
    assert data["is_enabled"] is False


def test_check_returns_singleton_id(client: Client) -> None:
    """Singleton ID in check endpoint must match the ID from list endpoint."""
    check_id = json.loads(client.get("/flags/dark_mode/check").content)["singleton_id"]
    list_id = json.loads(client.get("/flags/").content)["singleton_id"]
    assert check_id == list_id


# ── GET /flags/experimental-dashboard/ (feature_required decorator) ───────────


def test_experimental_dashboard_accessible_when_flag_enabled(client: Client) -> None:
    response = client.get("/flags/experimental-dashboard/")
    assert response.status_code == 200


def test_experimental_dashboard_blocked_when_flag_disabled() -> None:
    """Disable the flag and verify the decorator returns 403."""
    manager = FeatureFlagManager()
    manager.set_override("experimental_dashboard", False)
    c = Client()
    response = c.get("/flags/experimental-dashboard/")
    assert response.status_code == 403
    manager.clear_override("experimental_dashboard")
