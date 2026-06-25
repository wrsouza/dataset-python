"""LockedState — too many failed login attempts; requires an explicit unlock."""

from __future__ import annotations

from typing import TYPE_CHECKING

from auth_session_fsm.domain.interfaces import SessionState

if TYPE_CHECKING:
    from auth_session_fsm.domain.entities import AuthSession


class LockedState(SessionState):
    """Login is blocked after exceeding the maximum number of failed attempts."""

    def unlock(self, ctx: AuthSession) -> None:
        from auth_session_fsm.infrastructure.states.anonymous import (  # noqa: PLC0415
            AnonymousState,
        )

        ctx.failed_attempts = 0
        ctx.transition_to(AnonymousState(), "unlock")

    def get_name(self) -> str:
        return "Locked"

    def get_allowed_transitions(self) -> list[str]:
        return ["unlock"]
