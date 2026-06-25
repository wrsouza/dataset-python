"""Shared pytest configuration for P3 auth Provider Factory tests."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import pytest

# Add src to path so imports work without installing the package.
src_path = str(Path(__file__).resolve().parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")


@pytest.fixture(autouse=True)
def _reset_shared_provider_state() -> Any:
    """Clear class-level session/revocation state between tests.

    EmailPasswordAuthProvider, OAuthGoogleAuthProvider and
    OAuthGithubAuthProvider keep their issued-token state at class level
    (shared across instances, simulating a shared session store). Reset it
    before/after every test so tests stay isolated from each other.
    """
    from auth.infrastructure.creators import (
        EmailPasswordAuthProvider,
        OAuthGithubAuthProvider,
        OAuthGoogleAuthProvider,
    )

    for provider_cls in (
        EmailPasswordAuthProvider,
        OAuthGoogleAuthProvider,
        OAuthGithubAuthProvider,
    ):
        provider_cls._sessions.clear()
        provider_cls._revoked.clear()
    yield
    for provider_cls in (
        EmailPasswordAuthProvider,
        OAuthGoogleAuthProvider,
        OAuthGithubAuthProvider,
    ):
        provider_cls._sessions.clear()
        provider_cls._revoked.clear()
