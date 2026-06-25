"""PausedState — the user paused an in-progress download."""

from __future__ import annotations

from typing import TYPE_CHECKING

from download_manager_fsm.domain.interfaces import DownloadState

if TYPE_CHECKING:
    from download_manager_fsm.domain.entities import DownloadJob


class PausedState(DownloadState):
    """Transfer is suspended; can resume or be abandoned (retry resets to idle)."""

    def resume(self, ctx: DownloadJob) -> None:
        from download_manager_fsm.infrastructure.states.downloading import (  # noqa: PLC0415
            DownloadingState,
        )

        ctx.transition_to(DownloadingState(), "resume")

    def retry(self, ctx: DownloadJob) -> None:
        from download_manager_fsm.infrastructure.states.idle import (  # noqa: PLC0415
            IdleState,
        )

        ctx.transition_to(IdleState(), "retry")

    def get_name(self) -> str:
        return "Paused"

    def get_allowed_transitions(self) -> list[str]:
        return ["resume", "retry"]
