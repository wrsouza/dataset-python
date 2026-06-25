"""Typer CLI exposing the Game Particle System (Flyweight pattern).

The CLI is the client: it spawns particles via `SpawnExplosionUseCase`,
advances them via `RunSimulationUseCase`, and reports memory economy via
`GenerateMemoryReportUseCase` — all through abstractions, never touching
`ParticleTypeFactory` internals or a concrete physics class directly except
at this top-level wiring point.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import typer

from particle_system.application.use_cases import (
    ExportSimulationStateUseCase,
    GenerateMemoryReportUseCase,
    RunSimulationUseCase,
    SpawnExplosionUseCase,
)
from particle_system.domain.entities import Particle
from particle_system.domain.interfaces import PhysicsProtocol
from particle_system.infrastructure.factory import ParticleTypeFactory
from particle_system.infrastructure.physics import (
    SimpleGravityPhysics,
    WeightlessPhysics,
)

app = typer.Typer(
    name="particle-system",
    help="Simulate a game particle explosion to demonstrate the Flyweight pattern.",
)

DEFAULT_TYPE_NAMES = ["fire", "spark", "smoke"]
DEFAULT_DELTA_SECONDS = 0.1
LAST_RUN_STATE_PATH = Path(".particle_system_last_run.json")


def _build_physics(physics_name: str) -> PhysicsProtocol:
    """Select a concrete physics implementation by name (CLI wiring point)."""
    if physics_name == "weightless":
        return WeightlessPhysics()
    return SimpleGravityPhysics()


def _save_state(particles: list[Particle]) -> None:
    """Persist particle state between CLI invocations (simulate -> stats/export)."""
    payload = [particle.to_dict() for particle in particles]
    LAST_RUN_STATE_PATH.write_text(json.dumps(payload), encoding="utf-8")


def _load_state(factory: ParticleTypeFactory) -> list[Particle]:
    """Reload particle state saved by the most recent `simulate` invocation."""
    if not LAST_RUN_STATE_PATH.exists():
        return []
    raw = json.loads(LAST_RUN_STATE_PATH.read_text(encoding="utf-8"))
    return [
        Particle(
            x=item["x"],
            y=item["y"],
            vx=item["vx"],
            vy=item["vy"],
            age_seconds=item["age_seconds"],
            particle_type=factory.get_or_create(item["type"]),
        )
        for item in raw
    ]


@app.command()
def simulate(
    particles: int = typer.Option(1000, help="Number of particles to spawn."),
    steps: int = typer.Option(20, help="Number of physics steps to run."),
    physics: str = typer.Option(
        "gravity", help="Physics model: 'gravity' or 'weightless'."
    ),
    seed: int = typer.Option(42, help="Random seed for reproducible spawns."),
) -> None:
    """Spawn an explosion of PARTICLES particles and run STEPS physics steps."""
    factory = ParticleTypeFactory()
    spawn_use_case = SpawnExplosionUseCase(factory=factory)
    run_use_case = RunSimulationUseCase(physics=_build_physics(physics))

    population = spawn_use_case.execute(
        count=particles,
        type_names=DEFAULT_TYPE_NAMES,
        rng=random.Random(seed),
    )
    survivors = run_use_case.execute(
        population, steps=steps, delta_seconds=DEFAULT_DELTA_SECONDS
    )
    _save_state(survivors)

    typer.echo(f"Spawned {particles} particles using physics={physics!r}.")
    typer.echo(f"After {steps} steps: {len(survivors)} particles still alive.")
    typer.echo(
        f"Unique ParticleType flyweights in cache: {factory.get_flyweight_count()}"
    )


@app.command()
def stats() -> None:
    """Show the Flyweight memory economy report for the last simulation run."""
    factory = ParticleTypeFactory()
    survivors = _load_state(factory)
    if not survivors:
        typer.echo("No simulation data found. Run `simulate` first.", err=True)
        raise typer.Exit(code=1)

    report_use_case = GenerateMemoryReportUseCase(factory=factory)
    report = report_use_case.execute(survivors)

    typer.echo(f"Total particles:      {report.total_particles}")
    typer.echo(
        f"Unique flyweights:    {report.unique_flyweights} {report.flyweight_names}"
    )
    typer.echo(f"Bytes without Flyweight: {report.estimated_bytes_without_flyweight:,}")
    typer.echo(f"Bytes with Flyweight:    {report.estimated_bytes_with_flyweight:,}")
    typer.echo(f"Bytes saved:             {report.memory_saved_bytes:,}")
    typer.echo(f"Savings:                 {report.savings_percentage:.2f}%")


@app.command()
def export(
    output: Path = typer.Argument(..., help="Path to write the JSON export."),
) -> None:
    """Export the particle state from the last `simulate` run to OUTPUT as JSON."""
    factory = ParticleTypeFactory()
    survivors = _load_state(factory)
    if not survivors:
        typer.echo("No simulation data found. Run `simulate` first.", err=True)
        raise typer.Exit(code=1)

    export_use_case = ExportSimulationStateUseCase()
    count = export_use_case.execute(survivors, output)
    typer.echo(f"Exported {count} particles to {output}")


if __name__ == "__main__":
    app()
