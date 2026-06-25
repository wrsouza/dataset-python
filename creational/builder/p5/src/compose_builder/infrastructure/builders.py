"""Concrete Builder implementations for docker-compose generation."""

from __future__ import annotations

from typing import Any

from compose_builder.domain.entities import (
    ComposeFile,
    NetworkDefinition,
    ServiceDefinition,
    VolumeDefinition,
)
from compose_builder.domain.interfaces import DockerComposeBuilder

# ---------------------------------------------------------------------------
# Base builder — shared implementation
# ---------------------------------------------------------------------------


class _BaseComposeBuilder(DockerComposeBuilder):
    """Shared implementation of DockerComposeBuilder.

    Subclasses provide stack-specific defaults but share the same
    accumulation + build logic.
    """

    DEFAULT_VERSION = "3.9"

    def __init__(self) -> None:
        self._version: str = self.DEFAULT_VERSION
        self._services: dict[str, ServiceDefinition] = {}
        self._volumes: dict[str, VolumeDefinition] = {}
        self._networks: dict[str, NetworkDefinition] = {}

    # ------------------------------------------------------------------
    # Builder interface
    # ------------------------------------------------------------------

    def set_version(self, version: str) -> DockerComposeBuilder:
        self._version = version
        return self

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
        self._services[name] = ServiceDefinition(
            name=name,
            image=image,
            ports=ports or [],
            environment=env or {},
            volumes=volumes or [],
            depends_on=depends_on or [],
            healthcheck=healthcheck,
            networks=networks or [],
            command=command,
        )
        return self

    def add_volume(self, name: str, driver: str = "local") -> DockerComposeBuilder:
        self._volumes[name] = VolumeDefinition(name=name, driver=driver)
        return self

    def add_network(self, name: str, driver: str = "bridge") -> DockerComposeBuilder:
        self._networks[name] = NetworkDefinition(name=name, driver=driver)
        return self

    def build(self) -> ComposeFile:
        if not self._services:
            raise ValueError("A compose file must have at least one service.")
        compose = ComposeFile(
            version=self._version,
            services=dict(self._services),
            volumes=dict(self._volumes),
            networks=dict(self._networks),
        )
        self.reset()
        return compose

    def reset(self) -> None:
        self._version = self.DEFAULT_VERSION
        self._services = {}
        self._volumes = {}
        self._networks = {}


# ---------------------------------------------------------------------------
# WebAppComposeBuilder — web-optimised defaults
# ---------------------------------------------------------------------------


class WebAppComposeBuilder(_BaseComposeBuilder):
    """ConcreteBuilder for web application stacks.

    Pre-configures sensible web defaults:
    - restart: always for the app service
    - exposes a default network called 'web'
    """

    def __init__(self) -> None:
        super().__init__()
        # Pre-configure a shared network for web services
        self.add_network("web", driver="bridge")

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
        # Web services join the 'web' network by default
        effective_networks = networks or ["web"]
        return super().add_service(
            name=name,
            image=image,
            ports=ports,
            env=env,
            volumes=volumes,
            depends_on=depends_on,
            healthcheck=healthcheck,
            networks=effective_networks,
            command=command,
        )


# ---------------------------------------------------------------------------
# DataPipelineComposeBuilder — data pipeline defaults
# ---------------------------------------------------------------------------


class DataPipelineComposeBuilder(_BaseComposeBuilder):
    """ConcreteBuilder for data pipeline stacks.

    Pre-configures:
    - a 'data' network
    - restart: on-failure for worker services
    """

    def __init__(self) -> None:
        super().__init__()
        self.add_network("data", driver="bridge")

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
        effective_networks = networks or ["data"]
        service = ServiceDefinition(
            name=name,
            image=image,
            ports=ports or [],
            environment=env or {},
            volumes=volumes or [],
            depends_on=depends_on or [],
            healthcheck=healthcheck,
            networks=effective_networks,
            restart="on-failure",
            command=command,
        )
        self._services[name] = service
        return self


# ---------------------------------------------------------------------------
# MicroservicesComposeBuilder — microservices defaults
# ---------------------------------------------------------------------------


class MicroservicesComposeBuilder(_BaseComposeBuilder):
    """ConcreteBuilder for microservices stacks.

    Pre-configures:
    - a 'microservices' network
    - healthchecks enforced on all services
    - restart: always
    """

    DEFAULT_HEALTHCHECK: dict[str, Any] = {
        "test": ["CMD", "wget", "-qO-", "http://localhost/health"],
        "interval": "30s",
        "timeout": "10s",
        "retries": 3,
        "start_period": "40s",
    }

    def __init__(self) -> None:
        super().__init__()
        self.add_network("microservices", driver="bridge")

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
        # Apply default healthcheck if caller didn't supply one
        effective_healthcheck = healthcheck or self.DEFAULT_HEALTHCHECK
        effective_networks = networks or ["microservices"]
        service = ServiceDefinition(
            name=name,
            image=image,
            ports=ports or [],
            environment=env or {},
            volumes=volumes or [],
            depends_on=depends_on or [],
            healthcheck=effective_healthcheck,
            networks=effective_networks,
            restart="always",
            command=command,
        )
        self._services[name] = service
        return self
