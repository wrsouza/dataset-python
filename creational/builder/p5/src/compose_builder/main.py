"""Typer CLI entry point for the Docker-Compose Generator."""

from __future__ import annotations

from pathlib import Path

import typer

from compose_builder.application.use_cases import (
    GenerateComposeUseCase,
    UnknownPresetError,
)

app = typer.Typer(
    name="compose-builder",
    help="Generate docker-compose.yml files from stack presets (Builder pattern demo).",
)


@app.command("list-presets")
def list_presets() -> None:
    """List all available stack presets and their description."""
    use_case = GenerateComposeUseCase()
    for name, description in use_case.list_presets().items():
        typer.echo(f"{name}: {description}")


@app.command("generate")
def generate(
    preset: str = typer.Option(
        ..., "--preset", "-p", help="Preset identifier, see 'list-presets'."
    ),
    output: Path = typer.Option(
        Path("docker-compose.generated.yml"),
        "--output",
        "-o",
        help="Path of the docker-compose.yml file to write.",
    ),
) -> None:
    """Generate a docker-compose.yml file from a preset and save it to disk."""
    use_case = GenerateComposeUseCase()
    try:
        written_path = use_case.generate_to_file(preset, output)
    except UnknownPresetError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"Wrote {written_path}")


@app.command("print")
def print_compose(
    preset: str = typer.Option(
        ..., "--preset", "-p", help="Preset identifier, see 'list-presets'."
    ),
) -> None:
    """Print the generated docker-compose YAML to stdout without writing a file."""
    use_case = GenerateComposeUseCase()
    try:
        yaml_text = use_case.generate_yaml(preset)
    except UnknownPresetError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(yaml_text)


if __name__ == "__main__":
    app()
