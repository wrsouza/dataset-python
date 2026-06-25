"""ExpiredState — the session timed out and requires a fresh login."""

from __future__ import annotations

from typing import TYPE_CHECKING

from auth_session_fsm.domain.entities import MAX_FAILED_ATTEMPTS
from auth_session_fsm.domain.interfaces import SessionState

if TYPE_CHECKING:
    from auth_session_fsm.domain.entities import AuthSession


class ExpiredState(SessionState):
    """Session has expired; the user must authenticate again."""

    def login(self, ctx: AuthSession, success: bool) -> None:
        if success:
            from auth_session_fsm.infrastructure.states.active import (  # noqa: PLC0415
                ActiveState,
            )

            ctx.failed_attempts = 0
            ctx.transition_to(ActiveState(), "login")
            return

        ctx.failed_attempts += 1
        if ctx.failed_attempts >= MAX_FAILED_ATTEMPTS:
            from auth_session_fsm.infrastructure.states.locked import (  # noqa: PLC0415
                LockedState,
            )

            ctx.transition_to(LockedState(), "login")

    def get_name(self) -> str:
        return "Expired"

    def get_allowed_transitions(self) -> list[str]:
        return ["login"]
