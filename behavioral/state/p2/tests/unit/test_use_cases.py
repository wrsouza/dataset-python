"""Unit tests for the User Auth Session FSM use cases."""

from __future__ import annotations

import pytest

from auth_session_fsm.application.use_cases import (
    ExpireSessionUseCase,
    GetSessionUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshSessionUseCase,
    UnlockSessionUseCase,
)
from auth_session_fsm.domain.interfaces import InvalidTransitionError
from auth_session_fsm.infrastructure.repository import RedisSessionRepository


def test_login_use_case_creates_and_persists_a_new_session(
    repository: RedisSessionRepository,
) -> None:
    use_case = LoginUseCase(repository)

    session = use_case.execute("s1", success=True)

    assert session.get_current_state_name() == "Active"
    assert repository.find_by_id("s1") is not None


def test_logout_use_case_persists_transition(
    repository: RedisSessionRepository,
) -> None:
    LoginUseCase(repository).execute("s1", success=True)

    session = LogoutUseCase(repository).execute("s1")

    assert session.get_current_state_name() == "Anonymous"


def test_refresh_use_case_persists_transition(
    repository: RedisSessionRepository,
) -> None:
    LoginUseCase(repository).execute("s1", success=True)

    session = RefreshSessionUseCase(repository).execute("s1")

    assert session.get_current_state_name() == "Active"


def test_expire_use_case_persists_transition(
    repository: RedisSessionRepository,
) -> None:
    LoginUseCase(repository).execute("s1", success=True)

    session = ExpireSessionUseCase(repository).execute("s1")

    assert session.get_current_state_name() == "Expired"


def test_unlock_use_case_persists_transition(
    repository: RedisSessionRepository,
) -> None:
    login = LoginUseCase(repository)
    for _ in range(3):
        login.execute("s1", success=False)

    session = UnlockSessionUseCase(repository).execute("s1")

    assert session.get_current_state_name() == "Anonymous"
    assert session.failed_attempts == 0


def test_get_session_use_case_returns_none_for_unknown_session(
    repository: RedisSessionRepository,
) -> None:
    assert GetSessionUseCase(repository).execute("unknown") is None


def test_logout_use_case_raises_for_already_anonymous_session(
    repository: RedisSessionRepository,
) -> None:
    with pytest.raises(InvalidTransitionError):
        LogoutUseCase(repository).execute("brand-new-session")
