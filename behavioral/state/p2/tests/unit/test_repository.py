"""Unit tests for RedisSessionRepository."""

from __future__ import annotations

from auth_session_fsm.domain.entities import AuthSession
from auth_session_fsm.infrastructure.repository import RedisSessionRepository


def test_save_and_find_round_trips_state_and_failed_attempts(
    repository: RedisSessionRepository,
) -> None:
    session = AuthSession(session_id="s1")
    session.login(success=False)
    repository.save(session)

    found = repository.find_by_id("s1")

    assert found is not None
    assert found.get_current_state_name() == "Anonymous"
    assert found.failed_attempts == 1


def test_find_returns_none_for_unknown_session(
    repository: RedisSessionRepository,
) -> None:
    assert repository.find_by_id("unknown") is None


def test_save_overwrites_existing_session_state(
    repository: RedisSessionRepository,
) -> None:
    session = AuthSession(session_id="s1")
    session.login(success=True)
    repository.save(session)

    session.logout()
    repository.save(session)

    found = repository.find_by_id("s1")
    assert found is not None
    assert found.get_current_state_name() == "Anonymous"
