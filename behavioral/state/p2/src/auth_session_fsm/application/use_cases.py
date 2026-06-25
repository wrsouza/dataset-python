"""Application use cases for the User Auth Session FSM.

Each use case has a single responsibility and depends only on
RedisSessionRepository's public contract — sessions not yet seen are
created on the fly, always starting in AnonymousState (DIP-friendly:
none of these use cases know which concrete states exist).
"""

from __future__ import annotations

from auth_session_fsm.domain.entities import AuthSession
from auth_session_fsm.infrastructure.repository import RedisSessionRepository


class LoginUseCase:
    def __init__(self, repository: RedisSessionRepository) -> None:
        self._repository = repository

    def execute(self, session_id: str, success: bool) -> AuthSession:
        session = self._repository.find_by_id(session_id) or AuthSession(session_id)
        session.login(success)
        self._repository.save(session)
        return session


class LogoutUseCase:
    def __init__(self, repository: RedisSessionRepository) -> None:
        self._repository = repository

    def execute(self, session_id: str) -> AuthSession:
        session = self._repository.find_by_id(session_id) or AuthSession(session_id)
        session.logout()
        self._repository.save(session)
        return session


class RefreshSessionUseCase:
    def __init__(self, repository: RedisSessionRepository) -> None:
        self._repository = repository

    def execute(self, session_id: str) -> AuthSession:
        session = self._repository.find_by_id(session_id) or AuthSession(session_id)
        session.refresh()
        self._repository.save(session)
        return session


class ExpireSessionUseCase:
    def __init__(self, repository: RedisSessionRepository) -> None:
        self._repository = repository

    def execute(self, session_id: str) -> AuthSession:
        session = self._repository.find_by_id(session_id) or AuthSession(session_id)
        session.expire()
        self._repository.save(session)
        return session


class UnlockSessionUseCase:
    def __init__(self, repository: RedisSessionRepository) -> None:
        self._repository = repository

    def execute(self, session_id: str) -> AuthSession:
        session = self._repository.find_by_id(session_id) or AuthSession(session_id)
        session.unlock()
        self._repository.save(session)
        return session


class GetSessionUseCase:
    def __init__(self, repository: RedisSessionRepository) -> None:
        self._repository = repository

    def execute(self, session_id: str) -> AuthSession | None:
        return self._repository.find_by_id(session_id)
