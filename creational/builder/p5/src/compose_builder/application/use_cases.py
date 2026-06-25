"""Use cases orchestrating Directors, Builders and YAML serialization."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from compose_builder.application.directors import (
    DjangoWithRedisDirector,
    FastAPIWithPostgresDirector,
    KafkaStackDirector,
    WebPostgresRedisDirector,
)
from compose_builder.domain.entities import ComposeFile
from compose_builder.domain.interfaces import DockerComposeBuilder
from compose_builder.infrastructure.builders import (
    DataPipelineComposeBuilder,
    MicroservicesComposeBuilder,
    WebAppComposeBuilder,
)
from compose_builder.infrastructure.yaml_writer import YamlComposeSerializer


class Preset(str, Enum):
    """Identifiers for the stack presets exposed by the CLI."""

    WEB_POSTGRES_REDIS = "web-postgres-redis"
    FASTAPI_POSTGRES = "fastapi-postgres"
    DJANGO_REDIS = "django-redis"
    KAFKA_STACK = "kafka-stack"


_PRESET_DESCRIPTIONS: dict[Preset, str] = {
    Preset.WEB_POSTGRES_REDIS: "Web app + PostgreSQL + Redis cache",
    Preset.FASTAPI_POSTGRES: "FastAPI app + PostgreSQL (optional Redis cache)",
    Preset.DJANGO_REDIS: "Django app + Redis + PostgreSQL (optional Celery worker)",
    Preset.KAFKA_STACK: "Zookeeper + Kafka broker (optional UI and Postgres sink)",
}


class UnknownPresetError(ValueError):
    """Raised when a requested preset identifier is not registered."""


class GenerateComposeUseCase:
    """Orchestrates Director + Builder + YAML serialization for a preset.

    SRP: this use case's single responsibility is wiring the right Director
    to the right Builder and delegating serialization to infrastructure.
    DIP: depends on the DockerComposeBuilder abstraction and on the
    serializer, never instantiating low-level details inline beyond the
    minimal factory mapping required to pick a preset.
    """

    def __init__(self, serializer: YamlComposeSerializer | None = None) -> None:
        self._serializer = serializer or YamlComposeSerializer()

    @staticmethod
    def list_presets() -> dict[str, str]:
        """Return available preset identifiers mapped to their description."""
        return {preset.value: desc for preset, desc in _PRESET_DESCRIPTIONS.items()}

    def _builder_for(self, preset: Preset) -> DockerComposeBuilder:
        if preset is Preset.WEB_POSTGRES_REDIS:
            return WebAppComposeBuilder()
        if preset is Preset.FASTAPI_POSTGRES:
            return WebAppComposeBuilder()
        if preset is Preset.DJANGO_REDIS:
            return WebAppComposeBuilder()
        return MicroservicesComposeBuilder()

    def generate(self, preset_name: str) -> ComposeFile:
        """Build a ComposeFile product for the given preset name."""
        try:
            preset = Preset(preset_name)
        except ValueError as exc:
            raise UnknownPresetError(f"Unknown preset: {preset_name!r}") from exc

        builder = self._builder_for(preset)

        if preset is Preset.WEB_POSTGRES_REDIS:
            return WebPostgresRedisDirector(builder).build()
        if preset is Preset.FASTAPI_POSTGRES:
            return FastAPIWithPostgresDirector(builder).build(include_redis=True)
        if preset is Preset.DJANGO_REDIS:
            return DjangoWithRedisDirector(builder).build(include_celery=True)
        return KafkaStackDirector(builder).build()

    def generate_yaml(self, preset_name: str) -> str:
        """Build a preset and render it directly to a YAML string."""
        compose = self.generate(preset_name)
        return self._serializer.to_yaml(compose)

    def generate_to_file(self, preset_name: str, output_path: Path) -> Path:
        """Build a preset and write the resulting YAML to ``output_path``."""
        compose = self.generate(preset_name)
        return self._serializer.write(compose, output_path)


class DataPipelinePresetUseCase:
    """Extra use case exposing the data-pipeline builder defaults directly.

    Demonstrates that new builder/preset combinations can be added (OCP)
    without touching GenerateComposeUseCase or any existing Director.
    """

    def __init__(self, serializer: YamlComposeSerializer | None = None) -> None:
        self._serializer = serializer or YamlComposeSerializer()

    def generate(
        self,
        *,
        worker_image: str = "etl-worker:latest",
        source_db_image: str = "postgres:16-alpine",
    ) -> ComposeFile:
        """Build a minimal data-pipeline stack: worker + source database."""
        builder = DataPipelineComposeBuilder()
        builder.set_version("3.9")
        builder.add_service(
            name="source-db",
            image=source_db_image,
            env={"POSTGRES_PASSWORD": "${POSTGRES_PASSWORD:-secret}"},
            volumes=["source_data:/var/lib/postgresql/data"],
        )
        builder.add_volume("source_data")
        builder.add_service(
            name="worker",
            image=worker_image,
            depends_on=["source-db"],
            command="python -m etl.run",
        )
        return builder.build()

    def generate_yaml(self) -> str:
        """Build the data-pipeline stack and render it as a YAML string."""
        return self._serializer.to_yaml(self.generate())
