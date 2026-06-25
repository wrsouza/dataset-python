"""Typer CLI — the Client in this Facade demo, talks only to MigrationFacade."""

from __future__ import annotations

from urllib.parse import urlparse

import typer

from migration.application.facade import MigrationFacade
from migration.domain.entities import ConnectionConfig
from migration.infrastructure.connection_factory import DriverConnectionFactory
from migration.infrastructure.extractor import BatchDataExtractor
from migration.infrastructure.loader import GenericDataLoader
from migration.infrastructure.schema_analyzer import GenericSchemaAnalyzer
from migration.infrastructure.transformer import TrimmingTypeTransformer

app = typer.Typer(help="Migrate tables between databases using the Facade pattern.")


class UnsupportedConnectionStringError(ValueError):
    def __init__(self, uri: str) -> None:
        super().__init__(f"Unsupported connection string: {uri!r}")


def parse_connection_string(uri: str) -> ConnectionConfig:
    """sqlite:///path.db | mysql://user:pass@host/db | postgresql://user:pass@host/db"""
    if uri.startswith("sqlite://"):
        return ConnectionConfig(dialect="sqlite", dsn=uri.removeprefix("sqlite://"))
    parsed = urlparse(uri)
    if parsed.scheme == "mysql":
        return ConnectionConfig(dialect="mysql", dsn=uri)
    if parsed.scheme in ("postgresql", "postgres"):
        return ConnectionConfig(dialect="postgresql", dsn=uri)
    raise UnsupportedConnectionStringError(uri)


def build_facade(dest_dialect: str) -> MigrationFacade:
    """Composition root: the only place that wires concrete subsystems together."""
    return MigrationFacade(
        connection_factory=DriverConnectionFactory(),
        schema_analyzer=GenericSchemaAnalyzer(),
        extractor=BatchDataExtractor(),
        transformer=TrimmingTypeTransformer(),
        loader=GenericDataLoader(dialect=dest_dialect),
    )


@app.command()
def migrate(
    source: str = typer.Option(..., "--from", help="Source connection string"),
    dest: str = typer.Option(..., "--to", help="Destination connection string"),
    tables: str = typer.Option(..., "--tables", help="Comma-separated table names"),
    batch_size: int = typer.Option(500, "--batch-size"),
) -> None:
    """Migrate the given tables from --from to --to."""
    source_config = parse_connection_string(source)
    dest_config = parse_connection_string(dest)
    table_list = [t.strip() for t in tables.split(",") if t.strip()]

    facade = build_facade(dest_config.dialect)
    report = facade.migrate(source_config, dest_config, table_list, batch_size)

    for result in report.tables:
        status = "OK" if result.succeeded else "FAILED"
        typer.echo(
            f"[{status}] {result.table_name}: "
            f"{result.rows_extracted} extracted, {result.rows_loaded} loaded"
        )
        for error in result.errors:
            typer.echo(f"  error: {error}")

    typer.echo(
        f"Migration {report.migration_id}: "
        f"{'SUCCESS' if report.success else 'ROLLED BACK'} "
        f"in {report.duration_seconds:.2f}s, {report.total_rows_loaded} rows total"
    )
    if not report.success:
        raise typer.Exit(code=1)


@app.command(name="dry-run")
def dry_run(
    source: str = typer.Option(..., "--from", help="Source connection string"),
    tables: str = typer.Option(..., "--tables", help="Comma-separated table names"),
) -> None:
    """Validate the source schema without writing anything anywhere."""
    source_config = parse_connection_string(source)
    table_list = [t.strip() for t in tables.split(",") if t.strip()]

    facade = build_facade(dest_dialect="sqlite")
    report = facade.dry_run(source_config, table_list)

    for issue in report.issues:
        typer.echo(f"[{issue.severity.upper()}] {issue.table_name}: {issue.message}")

    typer.echo("VALID" if report.is_valid else "INVALID")
    if not report.is_valid:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
