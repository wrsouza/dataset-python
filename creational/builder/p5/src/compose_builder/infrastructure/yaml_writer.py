"""YAML serialization adapter for ComposeFile products."""

from __future__ import annotations

from pathlib import Path

import yaml

from compose_builder.domain.entities import ComposeFile


class YamlComposeSerializer:
    """Serializes a ComposeFile product to YAML text and disk.

    SRP: this class only knows how to turn a ComposeFile into YAML bytes
    and persist them; it knows nothing about Builders or Directors.
    """

    def to_yaml(self, compose: ComposeFile) -> str:
        """Render the compose file as a YAML string."""
        return yaml.safe_dump(
            compose.to_dict(),
            sort_keys=False,
            default_flow_style=False,
        )

    def write(self, compose: ComposeFile, output_path: Path) -> Path:
        """Serialize the compose file and write it to ``output_path``."""
        content = self.to_yaml(compose)
        output_path.write_text(content, encoding="utf-8")
        return output_path
