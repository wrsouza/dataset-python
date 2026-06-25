"""Redis repository for AuthSession — persists the FSM's current state
name and failed_attempts counter as a Redis hash per session.

OCP: a new state only needs to be added to `_STATE_REGISTRY` for the
repository to be able to rehydrate it; no other infrastructure code
changes.
"""

from __future__ import annotations

from redis import Redis

from auth_session_fsm.domain.entities import AuthSession
from auth_session_fsm.domain.interfaces import SessionState
from auth_session_fsm.infrastructure.states.active import ActiveState
from auth_session_fsm.infrastructure.states.anonymous import AnonymousState
from auth_session_fsm.infrastructure.states.expired import ExpiredState
from auth_session_fsm.infrastructure.states.locked import LockedState

_STATE_REGISTRY: dict[str, type[SessionState]] = {
    "Anonymous": AnonymousState,
    "Active": ActiveState,
    "Locked": LockedState,
    "Expired": ExpiredState,
}


class RedisSessionRepository:
    def __init__(self, client: Redis) -> None:
        self._client = client

    def save(self, session: AuthSession) -> None:
        key = self._key(session.session_id)
        self._client.hset(
            key,
            mapping={
                "state": session.get_current_state_name(),
                "failed_attempts": session.failed_attempts,
            },
        )

    def find_by_id(self, session_id: str) -> AuthSession | None:
        key = self._key(session_id)
        data = self._client.hgetall(key)
        if not data:
            return None

        state_name = self._decode(data[b"state"] if b"state" in data else data["state"])
        failed_attempts = int(
            data[b"failed_attempts"]
            if b"failed_attempts" in data
            else data["failed_attempts"]
        )

        session = AuthSession(session_id=session_id, failed_attempts=failed_attempts)
        session._state = _STATE_REGISTRY[state_name]()  # noqa: SLF001
        return session

    @staticmethod
    def _key(session_id: str) -> str:
        return f"session:{session_id}"

    @staticmethod
    def _decode(value: str | bytes) -> str:
        return value.decode() if isinstance(value, bytes) else value
