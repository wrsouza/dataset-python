"""Typer CLI entry point for the Export Format Bridge.

Composition root: this is the only module that imports
`build_format_exporter` directly. The use case and `ReportExporter`
abstraction depend solely on the `FormatExporter` interface.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import typer
from rich.console import Console

from exporter.application.use_cases import ExportReportUseCase, ReportExporter
from exporter.domain.entities import Report, ReportColumn, ReportRow
from exporter.infrastructure.factory import build_format_exporter

app = typer.Typer(
    name="export-bridge",
    help="Demonstrates the Bridge pattern across report export formats.",
    no_args_is_help=True,
)
console = Console()

DEFAULT_OUTPUT_DIR = Path(os.environ.get("EXPORT_OUTPUT_DIR", "./exports"))

FormatOption = typer.Option(
    "csv",
    "--format",
    "-f",
    help="Export format: csv, json, xml or excel.",
)
OutputDirOption = typer.Option(
    DEFAULT_OUTPUT_DIR, "--output-dir", "-o", help="Directory to write the export."
)
TitleArgument = typer.Argument(..., help="Report title (used as the file name).")
DataFileArgument = typer.Argument(..., help="JSON file with columns and rows.")


def _load_report(title: str, data_file: Path) -> Report:
    """Read a JSON file of {columns, rows} into a Report entity."""
    raw = json.loads(data_file.read_text(encoding="utf-8"))
    columns = [ReportColumn(name=name, label=name.title()) for name in raw["columns"]]
    rows = [ReportRow(values=row) for row in raw["rows"]]
    return Report(title=title, columns=columns, rows=rows)


def _build_exporter(format_name: str) -> ReportExporter:
    try:
        format_exporter = build_format_exporter(format_name)
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    return ReportExporter(format_exporter)


@app.command()
def export(
    title: str = TitleArgument,
    data_file: Path = DataFileArgument,
    output_dir: Path = OutputDirOption,
    export_format: str = FormatOption,
) -> None:
    """Export a report (read from data_file) to the chosen format."""
    report = _load_report(title, data_file)
    exporter = _build_exporter(export_format)
    use_case = ExportReportUseCase(exporter)
    result = use_case.execute(report, output_dir)
    console.print(f"[green]Exported[/green] {result.format_name}: {result.to_dict()}")


@app.command("list-formats")
def list_formats() -> None:
    """List the export formats supported by this Bridge."""
    console.print("Supported formats: csv, json, xml, excel")


if __name__ == "__main__":
    app()
