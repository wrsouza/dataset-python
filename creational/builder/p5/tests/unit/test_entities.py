"""Unit tests for domain entities: ServiceDefinition, VolumeDefinition, etc."""

from __future__ import annotations

from compose_builder.domain.entities import (
    ComposeFile,
    NetworkDefinition,
    ServiceDefinition,
    VolumeDefinition,
)


def test_service_definition_to_dict_minimal() -> None:
    service = ServiceDefinition(name="web", image="nginx:latest")

    data = service.to_dict()

    assert data == {"image": "nginx:latest"}


def test_service_definition_to_dict_full() -> None:
    service = ServiceDefinition(
        name="web",
        image="nginx:latest",
        ports=["80:80"],
        environment={"ENV": "prod"},
        volumes=["data:/data"],
        depends_on=["db"],
        healthcheck={"test": ["CMD", "true"]},
        restart="always",
        networks=["web"],
        command="nginx -g 'daemon off;'",
    )

    data = service.to_dict()

    assert data["ports"] == ["80:80"]
    assert data["environment"] == {"ENV": "prod"}
    assert data["volumes"] == ["data:/data"]
    assert data["depends_on"] == ["db"]
    assert data["healthcheck"] == {"test": ["CMD", "true"]}
    assert data["restart"] == "always"
    assert data["networks"] == ["web"]
    assert data["command"] == "nginx -g 'daemon off;'"


def test_volume_definition_default_driver_omitted() -> None:
    volume = VolumeDefinition(name="data")

    assert volume.to_dict() == {}


def test_volume_definition_custom_driver_included() -> None:
    volume = VolumeDefinition(name="data", driver="nfs", driver_opts={"a": "b"})

    data = volume.to_dict()

    assert data["driver"] == "nfs"
    assert data["driver_opts"] == {"a": "b"}


def test_network_definition_external_flag() -> None:
    network = NetworkDefinition(name="ext", external=True)

    data = network.to_dict()

    assert data["external"] is True
    assert data["driver"] == "bridge"


def test_compose_file_to_dict_assembles_all_sections() -> None:
    compose = ComposeFile(
        version="3.9",
        services={"web": ServiceDefinition(name="web", image="nginx")},
        volumes={"data": VolumeDefinition(name="data")},
        networks={"net": NetworkDefinition(name="net")},
    )

    data = compose.to_dict()

    assert data["version"] == "3.9"
    assert "web" in data["services"]
    assert "data" in data["volumes"]
    assert "net" in data["networks"]


def test_compose_file_to_dict_omits_empty_sections() -> None:
    compose = ComposeFile(version="3.9")

    data = compose.to_dict()

    assert data == {"version": "3.9"}
