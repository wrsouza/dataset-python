"""CLI entry point: the Client of the Proxy pattern.

This module never imports boto3 nor RealS3File directly for the read path --
it depends on the FileResource Protocol via the use cases, and always talks
to a RemoteFileProxy instance, treating it exactly as it would the real
object (DIP + LSP in action).
"""

from __future__ import annotations

import os

import typer

from src.remote_files.application.use_cases import (
    CheckFileExistsUseCase,
    GetCacheStatsUseCase,
    ReadFileUseCase,
)
from src.remote_files.domain.exceptions import RemoteFileError
from src.remote_files.infrastructure.real_s3_file import RealS3File
from src.remote_files.infrastructure.remote_file_proxy import RemoteFileProxy

app = typer.Typer(
    name="remote-file-proxy",
    help="Inspect and read files stored in S3 through a lazy, caching Proxy.",
)

DEFAULT_BUCKET_ENV_VAR = "S3_BUCKET"


def _resolve_bucket(bucket: str | None) -> str:
    resolved = bucket or os.environ.get(DEFAULT_BUCKET_ENV_VAR)
    if not resolved:
        typer.echo(
            f"Error: no bucket provided and {DEFAULT_BUCKET_ENV_VAR} is not set",
            err=True,
        )
        raise typer.Exit(code=1)
    return resolved


def _build_proxy(bucket: str, key: str) -> RemoteFileProxy:
    real_subject = RealS3File(bucket=bucket, key=key)
    return RemoteFileProxy(real_subject=real_subject)


@app.command()
def read(
    key: str = typer.Argument(..., help="S3 object key to read."),
    bucket: str = typer.Option(
        None, "--bucket", "-b", help=f"S3 bucket (default: ${DEFAULT_BUCKET_ENV_VAR})"
    ),
) -> None:
    """Read a file's content through the proxy, printing its size in bytes."""
    resolved_bucket = _resolve_bucket(bucket)
    proxy = _build_proxy(resolved_bucket, key)
    try:
        content = ReadFileUseCase(resource=proxy).execute()
    except RemoteFileError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"Read {len(content)} bytes from '{key}'")


@app.command()
def check(
    key: str = typer.Argument(..., help="S3 object key to check."),
    bucket: str = typer.Option(
        None, "--bucket", "-b", help=f"S3 bucket (default: ${DEFAULT_BUCKET_ENV_VAR})"
    ),
) -> None:
    """Check whether a file exists in S3, without downloading its content."""
    resolved_bucket = _resolve_bucket(bucket)
    proxy = _build_proxy(resolved_bucket, key)
    try:
        metadata = CheckFileExistsUseCase(resource=proxy).execute()
    except RemoteFileError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    if metadata.exists:
        typer.echo(f"'{key}' exists ({metadata.size_bytes} bytes)")
    else:
        typer.echo(f"'{key}' does not exist")
        raise typer.Exit(code=1)


@app.command()
def stats(
    key: str = typer.Argument(..., help="S3 object key to read twice for the demo."),
    bucket: str = typer.Option(
        None, "--bucket", "-b", help=f"S3 bucket (default: ${DEFAULT_BUCKET_ENV_VAR})"
    ),
) -> None:
    """Read a file twice and report cache hit/miss statistics from the proxy."""
    resolved_bucket = _resolve_bucket(bucket)
    proxy = _build_proxy(resolved_bucket, key)
    read_use_case = ReadFileUseCase(resource=proxy)
    try:
        read_use_case.execute()
        read_use_case.execute()
    except RemoteFileError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    cache_stats = GetCacheStatsUseCase(proxy=proxy).execute()
    typer.echo(f"Cache hits: {cache_stats.cache_hits}")
    typer.echo(f"Cache misses: {cache_stats.cache_misses}")
    typer.echo(f"Bytes saved: {cache_stats.bytes_saved}")
    typer.echo(f"Hit ratio: {cache_stats.hit_ratio:.2f}")


if __name__ == "__main__":
    app()
