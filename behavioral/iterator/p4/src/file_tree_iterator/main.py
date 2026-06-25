"""CLI entry point — Typer-based depth-first file tree walker.

Composition root: the only place where the concrete OsFileSystemSource
is built. All use cases receive abstractions (DIP).

Usage:
    python -m file_tree_iterator.main tree /path/to/dir
    python -m file_tree_iterator.main summary /path/to/dir
"""

from __future__ import annotations

import typer

from file_tree_iterator.application.use_cases import (
    SummarizeTreeUseCase,
    WalkTreeUseCase,
)
from file_tree_iterator.infrastructure.filesystem_source import OsFileSystemSource

app = typer.Typer(
    name="file-tree-iterator",
    help="Iterator pattern demo: depth-first traversal of a directory tree.",
    add_completion=False,
)


@app.command()
def tree(path: str) -> None:
    """Print every file and directory under `path`, depth-first."""
    use_case = WalkTreeUseCase(OsFileSystemSource())
    for entry in use_case.execute(path):
        marker = "[dir] " if entry.is_directory else "[file]"
        typer.echo(
            f"{marker} {entry.path}"
            + ("" if entry.is_directory else f" ({entry.size} bytes)")
        )


@app.command()
def summary(path: str) -> None:
    """Print aggregate file/directory counts and total size under `path`."""
    use_case = SummarizeTreeUseCase(OsFileSystemSource())
    result = use_case.execute(path)

    typer.echo(f"Files:       {result.file_count}")
    typer.echo(f"Directories: {result.directory_count}")
    typer.echo(f"Total size:  {result.total_size_bytes} bytes")


if __name__ == "__main__":
    app()
