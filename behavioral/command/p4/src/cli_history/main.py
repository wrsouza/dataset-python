"""CLI entry point — Typer-based to-do list with command history and replay.

Composition root: the only place where the concrete SQLite connection
is built. All use cases receive abstractions (DIP).

Usage:
    python -m cli_history.main add "Buy milk"
    python -m cli_history.main remove "Buy milk"
    python -m cli_history.main undo
    python -m cli_history.main list
    python -m cli_history.main history
    python -m cli_history.main replay
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

import typer

from cli_history.application.use_cases import (
    ExecuteCommandUseCase,
    GetHistoryUseCase,
    ReplayHistoryUseCase,
    UndoLastCommandUseCase,
)
from cli_history.domain.entities import TodoList
from cli_history.infrastructure.factory import (
    build_connection,
    build_log_repository,
    build_state_repository,
)

app = typer.Typer(
    name="cli-history",
    help="Command pattern demo: a to-do list with full history and replay.",
    add_completion=False,
)


@contextmanager
def _connection() -> Iterator[sqlite3.Connection]:
    connection = build_connection()
    try:
        yield connection
    finally:
        connection.close()


def _print_state(label: str, state: TodoList) -> None:
    typer.echo(typer.style(label, bold=True))
    if not state.items:
        typer.echo("  (empty)")
    for index, item in enumerate(state.items, start=1):
        typer.echo(f"  {index}. {item}")


@app.command()
def add(item: str) -> None:
    """Add an item to the to-do list."""
    with _connection() as connection:
        use_case = ExecuteCommandUseCase(
            build_state_repository(connection), build_log_repository(connection)
        )
        state = use_case.execute("add", {"item": item})
    _print_state("Current list:", state)


@app.command()
def remove(item: str) -> None:
    """Remove an item from the to-do list."""
    with _connection() as connection:
        use_case = ExecuteCommandUseCase(
            build_state_repository(connection), build_log_repository(connection)
        )
        state = use_case.execute("remove", {"item": item})
    _print_state("Current list:", state)


@app.command(name="list")
def list_items() -> None:
    """Show the current to-do list."""
    with _connection() as connection:
        state = build_state_repository(connection).load()
    _print_state("Current list:", state)


@app.command()
def undo() -> None:
    """Undo the most recently executed command."""
    with _connection() as connection:
        use_case = UndoLastCommandUseCase(
            build_state_repository(connection), build_log_repository(connection)
        )
        state = use_case.execute()
    _print_state("Current list (after undo):", state)


@app.command()
def history() -> None:
    """Show every command ever executed, oldest first."""
    with _connection() as connection:
        use_case = GetHistoryUseCase(build_log_repository(connection))
        entries = use_case.execute()

    typer.echo(typer.style("Command history:", bold=True))
    for entry in entries:
        typer.echo(
            f"  [{entry.entry_id}] {entry.command_name} {entry.payload} "
            f"at {entry.executed_at.isoformat()}"
        )


@app.command()
def replay() -> None:
    """Rebuild the to-do list from scratch by replaying the full command log."""
    with _connection() as connection:
        use_case = ReplayHistoryUseCase(build_log_repository(connection))
        state = use_case.execute()
    _print_state("Replayed list (rebuilt from log):", state)


if __name__ == "__main__":
    app()
