"""ActiveState — an authenticated, live session."""

from __future__ import annotations

from typing import TYPE_CHECKING

from auth_session_fsm.domain.interfaces import SessionState

if TYPE_CHECKING:
    from auth_session_fsm.domain.entities import AuthSession


class ActiveState(SessionState):
    """User is authenticated and the session has not expired."""

    def logout(self, ctx: AuthSession) -> None:
        from auth_session_fsm.infrastructure.states.anonymous import (  # noqa: PLC0415
            AnonymousState,
        )

        ctx.transition_to(AnonymousState(), "logout")

    def refresh(self, ctx: AuthSession) -> None:
        # Re-entrant: stays Active, but is recorded so the TTL/last-activity
        # timestamp can be derived from the transition history.
        ctx.transition_to(ActiveState(), "refresh")

    def expire(self, ctx: AuthSession) -> None:
        from auth_session_fsm.infrastructure.states.expired import (  # noqa: PLC0415
            ExpiredState,
        )

        ctx.transition_to(ExpiredState(), "expire")

    def get_name(self) -> str:
        return "Active"

    def get_allowed_transitions(self) -> list[str]:
        return ["logout", "refresh", "expire"]
