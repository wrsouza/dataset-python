"""CLI entry point — Typer-based code metrics analyzer.

Usage:
    python -m code_metrics_visitor.main analyze module.json --metric lines
    python -m code_metrics_visitor.main list-metrics

The module structure is read from a JSON file shaped like:
{
  "name": "my_module",
  "functions": [{"name": "f", "line_count": 5, "branch_count": 1,
                 "has_docstring": true}],
  "classes": [{"name": "C", "has_docstring": false, "methods": [...]}]
}
"""

from __future__ import annotations

from pathlib import Path

import typer

from code_metrics_visitor.application.use_cases import (
    AnalyzeModuleInput,
    AnalyzeModuleUseCase,
)
from code_metrics_visitor.domain.exceptions import InvalidMetricError
from code_metrics_visitor.infrastructure.visitors.registry import list_metric_names

app = typer.Typer(
    name="code-metrics",
    help="Visitor pattern demo: run metrics over a module's code structure.",
    add_completion=False,
)


@app.command()
def analyze(
    module_path: Path,
    metric: str = typer.Option("lines", "--metric", "-m"),
) -> None:
    """Run METRIC over the module described in MODULE_PATH (a JSON file)."""
    use_case = AnalyzeModuleUseCase()
    try:
        result = use_case.execute(
            AnalyzeModuleInput(module_path=module_path, metric_name=metric)
        )
    except InvalidMetricError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc

    for key, value in result.data.items():
        typer.echo(f"{key}: {value}")


@app.command(name="list-metrics")
def list_metrics() -> None:
    """List the names of every registered metric."""
    for name in list_metric_names():
        typer.echo(name)


if __name__ == "__main__":
    app()
