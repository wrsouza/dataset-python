"""The Component interface of the Composite pattern.

`BuildTask` is implemented both by atomic Leaf tasks (e.g. running a shell
command) and by `TaskGroup`, the Composite that holds child `BuildTask`s.
Client code (the CLI, the execution use case) only ever talks to this
interface, so it never needs to branch on "is this a leaf or a group?".
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.build_tasks.domain.entities import TaskResult


class BuildTask(ABC):
    """Component: anything that can be executed and report a TaskResult."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the human-readable name of this task."""

    @abstractmethod
    def execute(self) -> TaskResult:
        """Run this task (and, for composites, its children) and report."""

    @abstractmethod
    def estimated_duration_seconds(self) -> float:
        """Return the best-known estimate of how long this task will take."""
