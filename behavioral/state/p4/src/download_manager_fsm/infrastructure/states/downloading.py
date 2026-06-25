"""DownloadingState — the transfer is actively in progress."""

from __future__ import annotations

from typing import TYPE_CHECKING

from download_manager_fsm.domain.interfaces import DownloadState

if TYPE_CHECKING:
    from download_manager_fsm.domain.entities import DownloadJob


class DownloadingState(DownloadState):
    """Bytes are being transferred from S3."""

    def pause(self, ctx: DownloadJob) -> None:
        from download_manager_fsm.infrastructure.states.paused import (  # noqa: PLC0415
            PausedState,
        )

        ctx.transition_to(PausedState(), "pause")

    def complete(self, ctx: DownloadJob, bytes_downloaded: int) -> None:
        from download_manager_fsm.infrastructure.states.completed import (  # noqa: PLC0415
            CompletedState,
        )

        ctx.bytes_downloaded = bytes_downloaded
        ctx.transition_to(CompletedState(), "complete")

    def fail(self, ctx: DownloadJob, reason: str) -> None:
        from download_manager_fsm.infrastructure.states.failed import (  # noqa: PLC0415
            FailedState,
        )

        ctx.failure_reason = reason
        ctx.transition_to(FailedState(), "fail")

    def get_name(self) -> str:
        return "Downloading"

    def get_allowed_transitions(self) -> list[str]:
        return ["pause", "complete", "fail"]
