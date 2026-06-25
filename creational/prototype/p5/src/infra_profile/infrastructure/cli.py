"""Typer CLI exposing the Prototype-based infrastructure profile cloner.

Each command wires a use case to its dependencies (registry, repository)
and never contains business logic itself — that lives in
`src/infra_profile/application/use_cases.py`.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path

import typer

from src.infra_profile.application.use_cases import (
    CloneProfileUseCase,
    CreateProfileUseCase,
    ListSavedProfilesUseCase,
    ListTemplatesUseCase,
    SaveProfileUseCase,
    ShowProfileUseCase,
)
from src.infra_profile.domain.entities import StorageConfig
from src.infra_profile.infrastructure.json_repository import JsonProfileRepository
from src.infra_profile.infrastructure.registry import build_default_registry

DEFAULT_PROFILES_FILE = "profiles.json"

app = typer.Typer(
    name="infra-profile",
    help="Clone infrastructure profiles from prototype templates.",
)


def _resolve_repository() -> JsonProfileRepository:
    raw_path = os.getenv("PROFILES_FILE_PATH", DEFAULT_PROFILES_FILE)
    return JsonProfileRepository(Path(raw_path))


def _parse_pairs(pairs: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for pair in pairs:
        key, separator, value = pair.partition("=")
        if not separator:
            message = f"Invalid pair '{pair}', expected key=value"
            raise typer.BadParameter(message)
        parsed[key] = value
    return parsed


@app.command("list-templates")
def list_templates() -> None:
    """List every prototype template available for cloning."""
    use_case = ListTemplatesUseCase(registry=build_default_registry())
    for name in use_case.execute():
        typer.echo(name)


@app.command("clone")
def clone(
    template: str = typer.Argument(..., help="Name of the template to clone."),
    new_name: str = typer.Argument(..., help="Name for the new profile."),
    region: str = typer.Option(None, "--region", help="Override region."),
    instance_type: str = typer.Option(
        None, "--instance-type", help="Override instance type."
    ),
    tag: list[str] = typer.Option(
        [], "--tag", help="Replace tags entirely, as key=value pairs."
    ),
) -> None:
    """Clone TEMPLATE into a new profile NEW_NAME, then persist it."""
    overrides: dict[str, object] = {}
    if region is not None:
        overrides["region"] = region
    if instance_type is not None:
        overrides["instance_type"] = instance_type
    if tag:
        overrides["tags"] = _parse_pairs(tag)

    clone_use_case = CloneProfileUseCase(registry=build_default_registry())
    cloned = clone_use_case.execute(template, new_name, **overrides)

    save_use_case = SaveProfileUseCase(repository=_resolve_repository())
    save_use_case.execute(cloned)
    typer.echo(f"Cloned '{template}' -> '{new_name}' and saved.")


@app.command("create")
def create(
    name: str = typer.Argument(..., help="Name for the new profile."),
    instance_type: str = typer.Option(..., "--instance-type"),
    region: str = typer.Option(..., "--region"),
    storage_size_gb: int = typer.Option(20, "--storage-size-gb"),
) -> None:
    """Create a brand-new profile from scratch (no cloning) and persist it."""
    use_case = CreateProfileUseCase(repository=_resolve_repository())
    use_case.execute(
        name=name,
        instance_type=instance_type,
        region=region,
        storage=StorageConfig(size_gb=storage_size_gb),
    )
    typer.echo(f"Created profile '{name}'.")


@app.command("show")
def show(name: str = typer.Argument(..., help="Profile name to show.")) -> None:
    """Print a persisted profile as JSON-like key/value lines."""
    use_case = ShowProfileUseCase(repository=_resolve_repository())
    profile = use_case.execute(name)
    if profile is None:
        typer.echo(f"Profile '{name}' not found.")
        raise typer.Exit(code=1)
    for key, value in asdict(profile).items():
        typer.echo(f"{key}: {value}")


@app.command("export")
def export(
    name: str = typer.Argument(..., help="Profile name to export."),
    output: Path = typer.Option(..., "--output", help="Destination JSON file."),
) -> None:
    """Export a single persisted profile to a standalone JSON file."""
    use_case = ShowProfileUseCase(repository=_resolve_repository())
    profile = use_case.execute(name)
    if profile is None:
        typer.echo(f"Profile '{name}' not found.")
        raise typer.Exit(code=1)
    output.write_text(json.dumps(asdict(profile), indent=2), encoding="utf-8")
    typer.echo(f"Exported '{name}' to {output}")


@app.command("list")
def list_saved() -> None:
    """List every profile currently persisted in the repository."""
    use_case = ListSavedProfilesUseCase(repository=_resolve_repository())
    for profile in use_case.execute():
        typer.echo(f"{profile.name} ({profile.instance_type}, {profile.region})")


if __name__ == "__main__":
    app()
