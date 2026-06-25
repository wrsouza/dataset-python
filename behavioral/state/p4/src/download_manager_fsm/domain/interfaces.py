"""Domain interfaces for the Download Manager State machine.

Defines the State ABC following the State pattern.
OCP: adding a new state requires only a new class, no modification of
existing code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from download_manager_fsm.domain.entities import DownloadJob


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    def __init__(self, from_state: str, action: str) -> None:
        self.from_state = from_state
        self.action = action
        super().__init__(
            f"Cannot perform '{action}' on download in state '{from_state}'."
        )


class DownloadState(ABC):
    """Abstract base for all download job states.

    Each concrete state implements only the transitions it allows;
    invalid transitions raise InvalidTransitionError by default.
    """

    def start(self, ctx: DownloadJob) -> None:
        raise InvalidTransitionError(self.get_name(), "start")

    def pause(self, ctx: DownloadJob) -> None:
        raise InvalidTransitionError(self.get_name(), "pause")

    def resume(self, ctx: DownloadJob) -> None:
        raise InvalidTransitionError(self.get_name(), "resume")

    def complete(self, ctx: DownloadJob, bytes_downloaded: int) -> None:
        raise InvalidTransitionError(self.get_name(), "complete")

    def fail(self, ctx: DownloadJob, reason: str) -> None:
        raise InvalidTransitionError(self.get_name(), "fail")

    def retry(self, ctx: DownloadJob) -> None:
        raise InvalidTransitionError(self.get_name(), "retry")

    @abstractmethod
    def get_name(self) -> str:
        """Return the canonical name of this state."""

    @abstractmethod
    def get_allowed_transitions(self) -> list[str]:
        """Return the list of allowed action names from this state."""
