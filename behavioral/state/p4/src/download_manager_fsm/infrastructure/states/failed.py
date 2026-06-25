"""FailedState — the transfer errored out; can be retried from scratch."""

from __future__ import annotations

from typing import TYPE_CHECKING

from download_manager_fsm.domain.interfaces import DownloadState

if TYPE_CHECKING:
    from download_manager_fsm.domain.entities import DownloadJob


class FailedState(DownloadState):
    """Download failed; the only way forward is to retry from Idle."""

    def retry(self, ctx: DownloadJob) -> None:
        from download_manager_fsm.infrastructure.states.idle import (  # noqa: PLC0415
            IdleState,
        )

        ctx.transition_to(IdleState(), "retry")

    def get_name(self) -> str:
        return "Failed"

    def get_allowed_transitions(self) -> list[str]:
        return ["retry"]
