"""CLI entry point — Typer-based text editor with undo/redo via Memento.

Composition root: the only place where the concrete SQLite connection
is built. All use cases receive abstractions (DIP).

Usage:
    python -m text_editor_memento.main write "Hello, world"
    python -m text_editor_memento.main undo
    python -m text_editor_memento.main redo
    python -m text_editor_memento.main show
    python -m text_editor_memento.main history
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

import typer

from text_editor_memento.application.use_cases import (
    GetCurrentContentUseCase,
    GetHistoryUseCase,
    RedoEditUseCase,
    UndoEditUseCase,
    WriteContentUseCase,
)
from text_editor_memento.domain.entities import NoHistoryError
from text_editor_memento.infrastructure.factory import build_connection
from text_editor_memento.infrastructure.sqlite_caretaker import SqliteEditorCaretaker

app = typer.Typer(
    name="text-editor",
    help="Memento pattern demo: a text editor with undo/redo history.",
    add_completion=False,
)


@contextmanager
def _connection() -> Iterator[sqlite3.Connection]:
    connection = build_connection()
    try:
        yield connection
    finally:
        connection.close()


@app.command()
def write(content: str) -> None:
    """Replace the document's content, snapshotting the result."""
    with _connection() as connection:
        use_case = WriteContentUseCase(SqliteEditorCaretaker(connection))
        snapshot = use_case.execute(content)
    typer.echo(f"v{snapshot.version}: {snapshot.content}")


@app.command()
def undo() -> None:
    """Revert to the previous snapshot."""
    with _connection() as connection:
        use_case = UndoEditUseCase(SqliteEditorCaretaker(connection))
        try:
            snapshot = use_case.execute()
        except NoHistoryError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from exc
    typer.echo(f"v{snapshot.version}: {snapshot.content}")


@app.command()
def redo() -> None:
    """Re-apply the next snapshot that was previously undone."""
    with _connection() as connection:
        use_case = RedoEditUseCase(SqliteEditorCaretaker(connection))
        try:
            snapshot = use_case.execute()
        except NoHistoryError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from exc
    typer.echo(f"v{snapshot.version}: {snapshot.content}")


@app.command()
def show() -> None:
    """Show the document's current content."""
    with _connection() as connection:
        use_case = GetCurrentContentUseCase(SqliteEditorCaretaker(connection))
        document = use_case.execute()
    typer.echo(document.content or "(empty)")


@app.command()
def history() -> None:
    """Show every snapshot ever recorded, oldest first."""
    with _connection() as connection:
        use_case = GetHistoryUseCase(SqliteEditorCaretaker(connection))
        snapshots = use_case.execute()

    typer.echo(typer.style("Snapshot history:", bold=True))
    for snapshot in snapshots:
        typer.echo(f"  v{snapshot.version}: {snapshot.content!r}")


if __name__ == "__main__":
    app()
