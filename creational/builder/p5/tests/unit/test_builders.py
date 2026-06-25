"""Unit tests for the fluent ConcreteBuilders."""

from __future__ import annotations

import pytest

from compose_builder.infrastructure.builders import (
    DataPipelineComposeBuilder,
    MicroservicesComposeBuilder,
    WebAppComposeBuilder,
)


def test_fluent_chaining_returns_self() -> None:
    builder = WebAppComposeBuilder()

    result = builder.set_version("3.9").add_service("web", "nginx").add_volume("data")

    assert result is builder


def test_web_app_builder_assigns_default_network() -> None:
    builder = WebAppComposeBuilder()

    builder.add_service("web", "nginx:latest")
    compose = builder.build()

    assert compose.services["web"].networks == ["web"]
    assert "web" in compose.networks


def test_web_app_builder_respects_explicit_networks() -> None:
    builder = WebAppComposeBuilder()

    builder.add_service("web", "nginx:latest", networks=["custom"])
    compose = builder.build()

    assert compose.services["web"].networks == ["custom"]


def test_build_without_services_raises() -> None:
    builder = WebAppComposeBuilder()

    with pytest.raises(ValueError, match="at least one service"):
        builder.build()


def test_build_resets_internal_state() -> None:
    builder = WebAppComposeBuilder()
    builder.add_service("web", "nginx:latest")

    builder.build()

    assert builder._services == {}
    assert builder._version == builder.DEFAULT_VERSION


def test_reset_clears_accumulated_state() -> None:
    builder = WebAppComposeBuilder()
    builder.set_version("2.0").add_service("web", "nginx").add_volume("data")

    builder.reset()

    assert builder._services == {}
    assert builder._volumes == {}
    assert builder._version == builder.DEFAULT_VERSION


def test_data_pipeline_builder_default_network_and_restart() -> None:
    builder = DataPipelineComposeBuilder()

    builder.add_service("worker", "etl:latest")
    compose = builder.build()

    service = compose.services["worker"]
    assert service.networks == ["data"]
    assert service.restart == "on-failure"


def test_microservices_builder_applies_default_healthcheck() -> None:
    builder = MicroservicesComposeBuilder()

    builder.add_service("svc", "svc:latest")
    compose = builder.build()

    service = compose.services["svc"]
    assert service.healthcheck == MicroservicesComposeBuilder.DEFAULT_HEALTHCHECK
    assert service.restart == "always"
    assert service.networks == ["microservices"]


def test_microservices_builder_respects_custom_healthcheck() -> None:
    builder = MicroservicesComposeBuilder()
    custom_healthcheck = {"test": ["CMD", "custom"]}

    builder.add_service("svc", "svc:latest", healthcheck=custom_healthcheck)
    compose = builder.build()

    assert compose.services["svc"].healthcheck == custom_healthcheck


def test_add_network_and_add_volume_store_definitions() -> None:
    builder = WebAppComposeBuilder()

    builder.add_network("extra", driver="overlay")
    builder.add_volume("vol", driver="nfs")
    builder.add_service("web", "nginx")
    compose = builder.build()

    assert "extra" in compose.networks
    assert compose.networks["extra"].driver == "overlay"
    assert "vol" in compose.volumes
    assert compose.volumes["vol"].driver == "nfs"
