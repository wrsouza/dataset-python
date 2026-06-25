"""Integration tests — generate a real docker-compose.yml file on disk."""

from __future__ import annotations

from pathlib import Path

import yaml

from compose_builder.application.use_cases import GenerateComposeUseCase


def test_generate_to_file_writes_valid_compose_yaml(tmp_path: Path) -> None:
    output_path = tmp_path / "docker-compose.generated.yml"
    use_case = GenerateComposeUseCase()

    written_path = use_case.generate_to_file("web-postgres-redis", output_path)

    assert written_path == output_path
    assert output_path.exists()

    with output_path.open(encoding="utf-8") as handle:
        parsed = yaml.safe_load(handle)

    assert parsed["version"] == "3.9"
    assert set(parsed["services"]) == {"db", "cache", "web"}
    assert parsed["services"]["web"]["depends_on"] == ["db", "cache"]
    assert "db_data" in parsed["volumes"]


def test_generate_to_file_kafka_stack_round_trip(tmp_path: Path) -> None:
    output_path = tmp_path / "kafka-compose.yml"
    use_case = GenerateComposeUseCase()

    use_case.generate_to_file("kafka-stack", output_path)

    parsed = yaml.safe_load(output_path.read_text(encoding="utf-8"))

    assert "kafka" in parsed["services"]
    assert "zookeeper" in parsed["services"]
    assert parsed["networks"]["kafka_net"]["driver"] == "bridge"
