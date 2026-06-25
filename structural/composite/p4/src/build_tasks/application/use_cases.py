"""Use cases orchestrating the build task domain.

These classes depend only on the abstract `BuildTask` interface (Dependency
Inversion): they have no idea whether a given node is a `ShellCommandTask`,
a `SimulatedTask`, or a `TaskGroup` containing dozens of nested children.
"""

from __future__ import annotations

from pathlib import Path

from src.build_tasks.domain.entities import ExecutionSummary
from src.build_tasks.domain.interfaces import BuildTask
from src.build_tasks.infrastructure.definition_parser import (
    build_task_tree,
    load_definition,
)


class BuildTaskTreeFromFileUseCase:
    """Reads a task definition file and builds the BuildTask tree."""

    def execute(self, definition_path: Path) -> BuildTask:
        """Parse `definition_path` and return its root BuildTask."""
        definition = load_definition(definition_path)
        return build_task_tree(definition)


class ExecuteBuildTaskUseCase:
    """Runs a BuildTask tree and aggregates the results into a summary."""

    def execute(self, task: BuildTask) -> ExecutionSummary:
        """Execute `task` (leaf or composite) and summarize the outcome."""
        result = task.execute()
        succeeded, failed = result.count_leaf_results()
        return ExecutionSummary(
            root_result=result,
            total_duration_seconds=result.duration_seconds,
            tasks_succeeded=succeeded,
            tasks_failed=failed,
        )
