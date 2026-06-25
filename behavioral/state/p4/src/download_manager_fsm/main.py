"""CLI entry point — Typer-based download manager State machine.

Composition root: the only place where the concrete SQLite connection
and S3 client are built. All use cases receive abstractions (DIP).

Usage:
    python -m download_manager_fsm.main start job-1 my-bucket/file.zip
    python -m download_manager_fsm.main pause job-1
    python -m download_manager_fsm.main resume job-1
    python -m download_manager_fsm.main complete job-1
    python -m download_manager_fsm.main fail job-1 "connection reset"
    python -m download_manager_fsm.main retry job-1
    python -m download_manager_fsm.main status job-1
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

import typer

from download_manager_fsm.application.use_cases import (
    CompleteDownloadUseCase,
    DownloadJobNotFoundError,
    FailDownloadUseCase,
    GetDownloadJobUseCase,
    PauseDownloadUseCase,
    ResumeDownloadUseCase,
    RetryDownloadUseCase,
    StartDownloadInput,
    StartDownloadUseCase,
)
from download_manager_fsm.domain.entities import DownloadJob
from download_manager_fsm.domain.interfaces import InvalidTransitionError
from download_manager_fsm.infrastructure.factory import (
    build_connection,
    build_s3_client,
)
from download_manager_fsm.infrastructure.sqlite_repository import (
    SqliteDownloadJobRepository,
)

app = typer.Typer(
    name="download-manager",
    help="State pattern demo: an S3 download manager with pause/resume/retry.",
    add_completion=False,
)


@contextmanager
def _connection() -> Iterator[sqlite3.Connection]:
    connection = build_connection()
    try:
        yield connection
    finally:
        connection.close()


def _print_job(job: DownloadJob) -> None:
    typer.echo(f"[{job.get_current_state_name()}] {job.job_id} ({job.s3_key})")


@app.command()
def start(job_id: str, s3_key: str) -> None:
    """Start (or restart) a download job."""
    with _connection() as connection:
        repository = SqliteDownloadJobRepository(connection)
        use_case = StartDownloadUseCase(repository)
        try:
            job = use_case.execute(StartDownloadInput(job_id=job_id, s3_key=s3_key))
        except InvalidTransitionError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from exc
    _print_job(job)


@app.command()
def pause(job_id: str) -> None:
    """Pause an in-progress download."""
    with _connection() as connection:
        repository = SqliteDownloadJobRepository(connection)
        try:
            job = PauseDownloadUseCase(repository).execute(job_id)
        except (DownloadJobNotFoundError, InvalidTransitionError) as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from exc
    _print_job(job)


@app.command()
def resume(job_id: str) -> None:
    """Resume a paused download."""
    with _connection() as connection:
        repository = SqliteDownloadJobRepository(connection)
        try:
            job = ResumeDownloadUseCase(repository).execute(job_id)
        except (DownloadJobNotFoundError, InvalidTransitionError) as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from exc
    _print_job(job)


@app.command()
def complete(job_id: str) -> None:
    """Mark a download as complete, fetching the object size from S3."""
    with _connection() as connection:
        repository = SqliteDownloadJobRepository(connection)
        use_case = CompleteDownloadUseCase(repository, build_s3_client())
        try:
            job = use_case.execute(job_id)
        except (DownloadJobNotFoundError, InvalidTransitionError) as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from exc
    typer.echo(f"Completed {job.bytes_downloaded} bytes.")
    _print_job(job)


@app.command()
def fail(job_id: str, reason: str) -> None:
    """Mark a download as failed, recording a reason."""
    with _connection() as connection:
        repository = SqliteDownloadJobRepository(connection)
        try:
            job = FailDownloadUseCase(repository).execute(job_id, reason)
        except (DownloadJobNotFoundError, InvalidTransitionError) as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from exc
    _print_job(job)


@app.command()
def retry(job_id: str) -> None:
    """Retry a failed or paused download, resetting it to Idle."""
    with _connection() as connection:
        repository = SqliteDownloadJobRepository(connection)
        try:
            job = RetryDownloadUseCase(repository).execute(job_id)
        except (DownloadJobNotFoundError, InvalidTransitionError) as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from exc
    _print_job(job)


@app.command()
def status(job_id: str) -> None:
    """Show the current state of a download job."""
    with _connection() as connection:
        repository = SqliteDownloadJobRepository(connection)
        job = GetDownloadJobUseCase(repository).execute(job_id)
    if job is None:
        typer.echo(f"Download job '{job_id}' not found")
        raise typer.Exit(code=1)
    _print_job(job)


if __name__ == "__main__":
    app()
