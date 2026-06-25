"""Abstract Builder interface for Docker-Compose Generator."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from compose_builder.domain.entities import ComposeFile


class DockerComposeBuilder(ABC):
    """Builder interface for constructing docker-compose files step by step.

    Each concrete builder pre-configures sensible defaults for a specific
    stack type (web app, data pipeline, microservices).

    SRP: this class owns only the compose-file construction contract.
    OCP: new stack types are added via new ConcreteBuilders, not modifications.
    DIP: Directors depend on this abstraction, not on concrete builders.
    """

    @abstractmethod
    def set_version(self, version: str) -> DockerComposeBuilder:
        """Set the docker-compose file version (e.g. '3.9')."""
        ...

    @abstractmethod
    def add_service(
        self,
        name: str,
        image: str,
        ports: list[str] | None = None,
        env: dict[str, str] | None = None,
        volumes: list[str] | None = None,
        depends_on: list[str] | None = None,
        healthcheck: dict[str, Any] | None = None,
        networks: list[str] | None = None,
        command: str | None = None,
    ) -> DockerComposeBuilder:
        """Add a service to the compose file."""
        ...

    @abstractmethod
    def add_volume(self, name: str, driver: str = "local") -> DockerComposeBuilder:
        """Declare a named volume."""
        ...

    @abstractmethod
    def add_network(self, name: str, driver: str = "bridge") -> DockerComposeBuilder:
        """Declare a named network."""
        ...

    @abstractmethod
    def build(self) -> ComposeFile:
        """Assemble and return the finished ComposeFile product."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Clear all accumulated state so the builder can be reused."""
        ...
