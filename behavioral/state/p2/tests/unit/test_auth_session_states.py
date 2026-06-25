"""Unit tests for the AuthSession State pattern implementation."""

from __future__ import annotations

import pytest

from auth_session_fsm.domain.entities import AuthSession
from auth_session_fsm.domain.interfaces import InvalidTransitionError


def test_new_session_starts_anonymous() -> None:
    session = AuthSession(session_id="s1")

    assert session.get_current_state_name() == "Anonymous"
    assert session.get_allowed_transitions() == ["login"]


def test_successful_login_transitions_to_active() -> None:
    session = AuthSession(session_id="s1")

    session.login(success=True)

    assert session.get_current_state_name() == "Active"
    assert session.failed_attempts == 0


def test_failed_login_increments_counter_without_changing_state() -> None:
    session = AuthSession(session_id="s1")

    session.login(success=False)

    assert session.get_current_state_name() == "Anonymous"
    assert session.failed_attempts == 1


def test_third_failed_login_locks_the_session() -> None:
    session = AuthSession(session_id="s1")

    session.login(success=False)
    session.login(success=False)
    session.login(success=False)

    assert session.get_current_state_name() == "Locked"
    assert session.failed_attempts == 3


def test_unlock_resets_failures_and_returns_to_anonymous() -> None:
    session = AuthSession(session_id="s1")
    for _ in range(3):
        session.login(success=False)

    session.unlock()

    assert session.get_current_state_name() == "Anonymous"
    assert session.failed_attempts == 0


def test_logout_returns_active_session_to_anonymous() -> None:
    session = AuthSession(session_id="s1")
    session.login(success=True)

    session.logout()

    assert session.get_current_state_name() == "Anonymous"


def test_refresh_keeps_session_active_and_records_history() -> None:
    session = AuthSession(session_id="s1")
    session.login(success=True)

    session.refresh()

    assert session.get_current_state_name() == "Active"
    assert session.history[-1].action == "refresh"


def test_expire_transitions_active_session_to_expired() -> None:
    session = AuthSession(session_id="s1")
    session.login(success=True)

    session.expire()

    assert session.get_current_state_name() == "Expired"


def test_login_from_expired_can_reauthenticate() -> None:
    session = AuthSession(session_id="s1")
    session.login(success=True)
    session.expire()

    session.login(success=True)

    assert session.get_current_state_name() == "Active"


def test_failed_logins_from_expired_eventually_lock_the_session() -> None:
    session = AuthSession(session_id="s1")
    session.login(success=True)
    session.expire()

    session.login(success=False)
    session.login(success=False)
    session.login(success=False)

    assert session.get_current_state_name() == "Locked"


def test_locked_session_rejects_login() -> None:
    session = AuthSession(session_id="s1")
    for _ in range(3):
        session.login(success=False)

    with pytest.raises(InvalidTransitionError):
        session.login(success=True)


def test_anonymous_session_rejects_logout() -> None:
    session = AuthSession(session_id="s1")

    with pytest.raises(InvalidTransitionError):
        session.logout()


def test_active_session_rejects_unlock() -> None:
    session = AuthSession(session_id="s1")
    session.login(success=True)

    with pytest.raises(InvalidTransitionError):
        session.unlock()
