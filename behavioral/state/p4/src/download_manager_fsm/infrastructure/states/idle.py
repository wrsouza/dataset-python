"""IdleState — initial state; the download has not started (or was retried)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from download_manager_fsm.domain.interfaces import DownloadState

if TYPE_CHECKING:
    from download_manager_fsm.domain.entities import DownloadJob


class IdleState(DownloadState):
    """No download is in progress yet."""

    def start(self, ctx: DownloadJob) -> None:
        from download_manager_fsm.infrastructure.states.downloading import (  # noqa: PLC0415
            DownloadingState,
        )

        ctx.transition_to(DownloadingState(), "start")

    def get_name(self) -> str:
        return "Idle"

    def get_allowed_transitions(self) -> list[str]:
        return ["start"]
