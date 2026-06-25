"""CompletedState — terminal state for a successfully finished download."""

from __future__ import annotations

from download_manager_fsm.domain.interfaces import DownloadState


class CompletedState(DownloadState):
    """Download finished successfully; no further transitions are allowed."""

    def get_name(self) -> str:
        return "Completed"

    def get_allowed_transitions(self) -> list[str]:
        return []
