"""The Composite implementation of `BuildTask`.

`TaskGroup` holds an ordered list of child `BuildTask`s — which may
themselves be `TaskGroup`s, allowing arbitrarily nested build pipelines
(e.g. `build_all` containing a `test_all` sub-group). `TaskGroup` is fully
substitutable for `BuildTask` (Liskov Substitution): client code that calls
`task.execute()` cannot tell, and does not need to tell, whether `task` is a
leaf or a group.
"""

from __future__ import annotations

import time

from src.build_tasks.domain.entities import TaskResult, TaskStatus
from src.build_tasks.domain.exceptions import DuplicateChildTaskError
from src.build_tasks.domain.interfaces import BuildTask


class TaskGroup(BuildTask):
    """Composite: a named collection of child BuildTasks run in sequence.

    Execution stops at the first failing child (fail-fast), matching how
    most real build tools behave: there is little point compiling tests
    against code that did not compile.
    """

    def __init__(self, name: str, *, stop_on_failure: bool = True) -> None:
        self._name = name
        self._stop_on_failure = stop_on_failure
        self._children: list[BuildTask] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def children(self) -> tuple[BuildTask, ...]:
        """Return the child tasks in execution order."""
        return tuple(self._children)

    def add(self, task: BuildTask) -> None:
        """Append a child task, rejecting duplicate names at this level."""
        if any(child.name == task.name for child in self._children):
            raise DuplicateChildTaskError(self._name, task.name)
        self._children.append(task)

    def estimated_duration_seconds(self) -> float:
        return sum(child.estimated_duration_seconds() for child in self._children)

    def execute(self) -> TaskResult:
        started_at = time.monotonic()
        children_results: list[TaskResult] = []
        overall_status = TaskStatus.SUCCESS

        for child in self._children:
            result = child.execute()
            children_results.append(result)
            if result.status == TaskStatus.FAILURE:
                overall_status = TaskStatus.FAILURE
                if self._stop_on_failure:
                    break

        duration = time.monotonic() - started_at
        return TaskResult(
            task_name=self._name,
            status=overall_status,
            duration_seconds=duration,
            children_results=tuple(children_results),
        )
