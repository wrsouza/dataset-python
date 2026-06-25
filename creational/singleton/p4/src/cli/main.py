"""Typer CLI exposing the StructuredLogger singleton to the terminal.

Demonstrates that every command, regardless of how it obtains the logger,
ends up writing through the exact same singleton instance.
"""

from __future__ import annotations

import os

import typer

from src.logger.application.use_cases import (
    EmitLogMessageUseCase,
    SetLoggerContextUseCase,
    get_logger,
)
from src.logger.domain.entities import LogLevel

app = typer.Typer(
    name="structured-logger",
    help="Structured JSON logger backed by a thread-safe Singleton.",
)

_LEVEL_NAMES: dict[str, LogLevel] = {level.label: level for level in LogLevel}


def _resolve_min_level() -> LogLevel:
    raw = os.getenv("LOG_LEVEL", "INFO").upper()
    return _LEVEL_NAMES.get(raw, LogLevel.INFO)


def _resolve_level(level: str) -> LogLevel:
    try:
        return _LEVEL_NAMES[level.upper()]
    except KeyError as exc:
        valid = ", ".join(_LEVEL_NAMES)
        message = f"Invalid level '{level}'. Valid options: {valid}"
        raise typer.BadParameter(message) from exc


@app.command()
def log(
    message: str = typer.Argument(..., help="Message to log."),
    level: str = typer.Option("INFO", "--level", "-l", help="Log severity."),
    tag: list[str] = typer.Option(
        [], "--tag", "-t", help="Extra context as key=value pairs."
    ),
) -> None:
    """Emit a single structured log line through the shared singleton."""
    log_level = _resolve_level(level)
    logger = get_logger(min_level=_resolve_min_level())
    extra_context = _parse_tags(tag)
    use_case = EmitLogMessageUseCase(logger=logger)
    use_case.execute(log_level, message, **extra_context)


@app.command()
def context(
    pairs: list[str] = typer.Argument(..., help="Global context as key=value pairs."),
) -> None:
    """Attach persistent context that future log calls will include."""
    logger = get_logger(min_level=_resolve_min_level())
    use_case = SetLoggerContextUseCase(logger=logger)
    use_case.execute(**_parse_tags(pairs))
    typer.echo(f"Context updated: {_parse_tags(pairs)}")


@app.command()
def stats() -> None:
    """Show aggregate counters from the singleton logger instance."""
    logger = get_logger(min_level=_resolve_min_level())
    typer.echo(
        f"records_emitted={logger.stats.records_emitted} "
        f"handler_count={logger.stats.handler_count} "
        f"by_level={logger.stats.records_by_level}"
    )


def _parse_tags(pairs: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for pair in pairs:
        key, _, value = pair.partition("=")
        if not _:
            message = f"Invalid tag '{pair}', expected key=value"
            raise typer.BadParameter(message)
        parsed[key] = value
    return parsed


if __name__ == "__main__":
    app()
