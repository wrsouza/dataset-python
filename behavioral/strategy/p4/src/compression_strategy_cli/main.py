"""CLI entry point — Typer-based file compressor with swappable codecs.

Usage:
    python -m compression_strategy_cli.main compress file.txt --strategy gzip
    python -m compression_strategy_cli.main decompress file.txt.gz --strategy gzip
    python -m compression_strategy_cli.main list-strategies
"""

from __future__ import annotations

from pathlib import Path

import typer

from compression_strategy_cli.application.use_cases import (
    CompressFileInput,
    CompressFileUseCase,
    DecompressFileInput,
    DecompressFileUseCase,
)
from compression_strategy_cli.domain.exceptions import InvalidStrategyError
from compression_strategy_cli.infrastructure.strategies.registry import (
    list_strategy_names,
)

app = typer.Typer(
    name="compression-cli",
    help="Strategy pattern demo: compress/decompress files with swappable codecs.",
    add_completion=False,
)


@app.command()
def compress(
    file: Path,
    strategy: str = typer.Option("gzip", "--strategy", "-s"),
) -> None:
    """Compress FILE using the given strategy."""
    use_case = CompressFileUseCase()
    try:
        output_path, result = use_case.execute(
            CompressFileInput(input_path=file, strategy_name=strategy)
        )
    except InvalidStrategyError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    typer.echo(
        f"Wrote {output_path} ({result.original_size} -> {result.output_size} bytes, "
        f"ratio {result.ratio:.2%})"
    )


@app.command()
def decompress(
    file: Path,
    strategy: str = typer.Option("gzip", "--strategy", "-s"),
) -> None:
    """Decompress FILE using the given strategy."""
    use_case = DecompressFileUseCase()
    try:
        output_path, result = use_case.execute(
            DecompressFileInput(input_path=file, strategy_name=strategy)
        )
    except InvalidStrategyError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    typer.echo(
        f"Wrote {output_path} ({result.original_size} -> {result.output_size} bytes)"
    )


@app.command(name="list-strategies")
def list_strategies() -> None:
    """List the names of every registered compression strategy."""
    for name in list_strategy_names():
        typer.echo(name)


if __name__ == "__main__":
    app()
