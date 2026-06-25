"""Shared test fixtures for P5 — Docker-Compose Generator CLI."""

from __future__ import annotations

import pytest

from compose_builder.infrastructure.builders import WebAppComposeBuilder
from compose_builder.infrastructure.yaml_writer import YamlComposeSerializer


@pytest.fixture
def web_builder() -> WebAppComposeBuilder:
    return WebAppComposeBuilder()


@pytest.fixture
def serializer() -> YamlComposeSerializer:
    return YamlComposeSerializer()
