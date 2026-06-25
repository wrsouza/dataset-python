"""Domain-specific exceptions for build task execution and definition."""

from __future__ import annotations


class BuildTaskError(Exception):
    """Base class for all build-task domain errors."""


class TaskExecutionError(BuildTaskError):
    """Raised when a task's underlying action fails during `execute()`."""

    def __init__(self, task_name: str, reason: str) -> None:
        self.task_name = task_name
        self.reason = reason
        super().__init__(f"Task '{task_name}' failed: {reason}")


class DuplicateChildTaskError(BuildTaskError):
    """Raised when a Composite gets a child whose name already exists."""

    def __init__(self, group_name: str, child_name: str) -> None:
        self.group_name = group_name
        self.child_name = child_name
        super().__init__(
            f"Group '{group_name}' already has a child named '{child_name}'"
        )


class TaskDefinitionError(BuildTaskError):
    """Raised when a task definition file cannot be parsed into a tree."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid task definition: {reason}")
