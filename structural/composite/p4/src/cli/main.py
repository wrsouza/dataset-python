"""Typer CLI exposing the BuildTask Composite tree to the terminal.

The CLI is the client of the Composite pattern: it loads a task definition
file, gets back a single `BuildTask` (which may be a deeply nested tree of
groups and leaves), and calls `execute()` on it exactly the same way
regardless of how many leaves are hiding underneath.
"""

from __future__ import annotations

from pathlib import Path

import typer

from src.build_tasks.application.use_cases import (
    BuildTaskTreeFromFileUseCase,
    ExecuteBuildTaskUseCase,
)
from src.build_tasks.domain.entities import TaskResult
from src.build_tasks.domain.exceptions import BuildTaskError

app = typer.Typer(
    name="build-tasks",
    help="Run nested build task trees defined in JSON or YAML (Composite pattern).",
)

INDENT_SPACES_PER_LEVEL = 2


@app.command()
def run(
    definition_file: Path = typer.Argument(
        ..., help="Path to a JSON or YAML build task definition file."
    ),
) -> None:
    """Build the task tree from DEFINITION_FILE and execute it."""
    try:
        task = BuildTaskTreeFromFileUseCase().execute(definition_file)
        summary = ExecuteBuildTaskUseCase().execute(task)
    except BuildTaskError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    _print_result_tree(summary.root_result, depth=0)
    typer.echo(
        f"\n{summary.overall_status.value.upper()} — "
        f"{summary.tasks_succeeded} succeeded, {summary.tasks_failed} failed, "
        f"{summary.total_duration_seconds:.3f}s total"
    )
    if summary.tasks_failed > 0:
        raise typer.Exit(code=1)


@app.command()
def describe(
    definition_file: Path = typer.Argument(
        ..., help="Path to a JSON or YAML build task definition file."
    ),
) -> None:
    """Show the task tree and its estimated duration without running it."""
    try:
        task = BuildTaskTreeFromFileUseCase().execute(definition_file)
    except BuildTaskError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"{task.name} (estimated {task.estimated_duration_seconds():.2f}s)")


def _print_result_tree(result: TaskResult, depth: int) -> None:
    indent = " " * (depth * INDENT_SPACES_PER_LEVEL)
    marker = "OK" if result.is_success else "FAIL"
    duration = result.duration_seconds
    typer.echo(f"{indent}[{marker}] {result.task_name} ({duration:.3f}s)")
    for child in result.children_results:
        _print_result_tree(child, depth + 1)


if __name__ == "__main__":
    app()
