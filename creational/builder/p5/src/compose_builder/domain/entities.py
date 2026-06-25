"""Domain entities for the Docker-Compose Generator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ServiceDefinition:
    """Represents a single docker-compose service."""

    name: str
    image: str
    ports: list[str] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    volumes: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    healthcheck: dict[str, Any] | None = None
    restart: str = "unless-stopped"
    networks: list[str] = field(default_factory=list)
    command: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to docker-compose service dict (only non-empty fields)."""
        data: dict[str, Any] = {"image": self.image}

        if self.ports:
            data["ports"] = self.ports
        if self.environment:
            data["environment"] = self.environment
        if self.volumes:
            data["volumes"] = self.volumes
        if self.depends_on:
            data["depends_on"] = self.depends_on
        if self.healthcheck:
            data["healthcheck"] = self.healthcheck
        if self.restart != "unless-stopped":
            data["restart"] = self.restart
        if self.networks:
            data["networks"] = self.networks
        if self.command:
            data["command"] = self.command

        return data


@dataclass
class VolumeDefinition:
    """Represents a named docker-compose volume."""

    name: str
    driver: str = "local"
    driver_opts: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if self.driver != "local":
            data["driver"] = self.driver
        if self.driver_opts:
            data["driver_opts"] = self.driver_opts
        return data


@dataclass
class NetworkDefinition:
    """Represents a named docker-compose network."""

    name: str
    driver: str = "bridge"
    external: bool = False

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"driver": self.driver}
        if self.external:
            data["external"] = True
        return data


@dataclass
class ComposeFile:
    """Product: a fully assembled docker-compose configuration.

    Renders to a valid YAML string suitable for writing to disk.
    """

    version: str
    services: dict[str, ServiceDefinition] = field(default_factory=dict)
    volumes: dict[str, VolumeDefinition] = field(default_factory=dict)
    networks: dict[str, NetworkDefinition] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Produce the full compose dict for YAML serialisation."""
        data: dict[str, Any] = {"version": self.version}

        if self.services:
            data["services"] = {
                name: svc.to_dict() for name, svc in self.services.items()
            }

        if self.volumes:
            data["volumes"] = {
                name: vol.to_dict() for name, vol in self.volumes.items()
            }

        if self.networks:
            data["networks"] = {
                name: net.to_dict() for name, net in self.networks.items()
            }

        return data
