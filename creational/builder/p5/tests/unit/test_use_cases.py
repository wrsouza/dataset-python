"""Unit tests for application use cases — fully in-memory, no disk access."""

from __future__ import annotations

import pytest

from compose_builder.application.use_cases import (
    DataPipelinePresetUseCase,
    GenerateComposeUseCase,
    UnknownPresetError,
)


def test_list_presets_returns_all_known_presets() -> None:
    presets = GenerateComposeUseCase.list_presets()

    assert "web-postgres-redis" in presets
    assert "fastapi-postgres" in presets
    assert "django-redis" in presets
    assert "kafka-stack" in presets


def test_generate_web_postgres_redis_preset() -> None:
    use_case = GenerateComposeUseCase()

    compose = use_case.generate("web-postgres-redis")

    assert set(compose.services) == {"db", "cache", "web"}


def test_generate_unknown_preset_raises() -> None:
    use_case = GenerateComposeUseCase()

    with pytest.raises(UnknownPresetError):
        use_case.generate("does-not-exist")


def test_generate_yaml_returns_parseable_string() -> None:
    use_case = GenerateComposeUseCase()

    text = use_case.generate_yaml("kafka-stack")

    assert "services:" in text


def test_data_pipeline_preset_use_case_generates_worker_and_db() -> None:
    use_case = DataPipelinePresetUseCase()

    compose = use_case.generate()

    assert set(compose.services) == {"source-db", "worker"}


def test_data_pipeline_preset_use_case_generate_yaml() -> None:
    use_case = DataPipelinePresetUseCase()

    text = use_case.generate_yaml()

    assert "worker" in text
