"""Entities and value objects for the build task domain.

`TaskResult` is the uniform return type produced by both Leaf and Composite
tasks — the Composite pattern's transparency relies on every node, simple or
grouped, reporting outcomes through this same shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(str, Enum):  # noqa: UP042
    """Outcome of executing a single build task."""

    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class TaskResult:
    """Immutable record of how one task execution went.

    Composite nodes aggregate the `TaskResult`s of their children into a
    single `TaskResult` for themselves, so callers never need to know
    whether they are looking at a leaf or a group.
    """

    task_name: str
    status: TaskStatus
    duration_seconds: float
    message: str = ""
    children_results: tuple[TaskResult, ...] = field(default_factory=tuple)

    @property
    def is_success(self) -> bool:
        """Return True when this task (and all its children) succeeded."""
        return self.status == TaskStatus.SUCCESS

    def count_leaf_results(self) -> tuple[int, int]:
        """Return (succeeded, failed) counts across all leaf descendants.

        A result with no children is itself a leaf result.
        """
        if not self.children_results:
            succeeded = 1 if self.status == TaskStatus.SUCCESS else 0
            failed = 1 if self.status == TaskStatus.FAILURE else 0
            return succeeded, failed

        total_succeeded = 0
        total_failed = 0
        for child in self.children_results:
            child_succeeded, child_failed = child.count_leaf_results()
            total_succeeded += child_succeeded
            total_failed += child_failed
        return total_succeeded, total_failed


@dataclass(frozen=True)
class ExecutionSummary:
    """Aggregated report for a full build task tree execution."""

    root_result: TaskResult
    total_duration_seconds: float
    tasks_succeeded: int
    tasks_failed: int

    @property
    def overall_status(self) -> TaskStatus:
        """Return FAILURE if any leaf failed, otherwise SUCCESS."""
        if self.tasks_failed > 0:
            return TaskStatus.FAILURE
        return TaskStatus.SUCCESS
