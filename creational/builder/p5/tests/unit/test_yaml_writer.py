"""Unit tests for YAML serialization — no disk access."""

from __future__ import annotations

import yaml

from compose_builder.domain.entities import ComposeFile, ServiceDefinition
from compose_builder.infrastructure.yaml_writer import YamlComposeSerializer


def test_to_yaml_produces_parseable_yaml() -> None:
    compose = ComposeFile(
        version="3.9",
        services={"web": ServiceDefinition(name="web", image="nginx:latest")},
    )
    serializer = YamlComposeSerializer()

    text = serializer.to_yaml(compose)
    parsed = yaml.safe_load(text)

    assert parsed["version"] == "3.9"
    assert parsed["services"]["web"]["image"] == "nginx:latest"


def test_to_yaml_preserves_key_order_with_sort_keys_false() -> None:
    compose = ComposeFile(
        version="3.9",
        services={"web": ServiceDefinition(name="web", image="nginx:latest")},
    )
    serializer = YamlComposeSerializer()

    text = serializer.to_yaml(compose)

    assert text.startswith("version:")
