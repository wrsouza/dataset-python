"""JSON file-based implementation of `ProfileRepository`.

This is the only place in the codebase that knows profiles are stored as a
JSON file on disk. The application layer never imports this module
directly — it depends on the `ProfileRepository` Protocol instead, so this
adapter could be swapped for a database or cloud-API implementation without
touching any use case.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from src.infra_profile.domain.entities import InfrastructureProfile, StorageConfig


class JsonProfileRepository:
    """Stores `InfrastructureProfile` records as a single JSON file.

    Implements the `ProfileRepository` Protocol structurally (no explicit
    inheritance needed) by providing `save`, `get`, and `list_all`.
    """

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def save(self, profile: InfrastructureProfile) -> None:
        """Persist `profile`, replacing any existing entry with the same name."""
        records = self._read_all()
        records[profile.name] = asdict(profile)
        self._write_all(records)

    def get(self, name: str) -> InfrastructureProfile | None:
        """Return the profile stored under `name`, or None if absent."""
        records = self._read_all()
        raw = records.get(name)
        if raw is None:
            return None
        return self._deserialize(raw)

    def list_all(self) -> list[InfrastructureProfile]:
        """Return every profile currently persisted, sorted by name."""
        records = self._read_all()
        return [self._deserialize(raw) for _, raw in sorted(records.items())]

    def _read_all(self) -> dict[str, dict[str, object]]:
        if not self._file_path.exists():
            return {}
        content = self._file_path.read_text(encoding="utf-8").strip()
        if not content:
            return {}
        return json.loads(content)  # type: ignore[no-any-return]

    def _write_all(self, records: dict[str, dict[str, object]]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        self._file_path.write_text(
            json.dumps(records, indent=2, sort_keys=True), encoding="utf-8"
        )

    @staticmethod
    def _deserialize(raw: dict[str, object]) -> InfrastructureProfile:
        storage_raw = raw["storage"]
        tags_raw = raw["tags"]
        firewall_rules_raw = raw["firewall_rules"]
        env_vars_raw = raw["env_vars"]
        if not isinstance(storage_raw, dict):
            message = "Malformed profile record: 'storage' must be an object"
            raise ValueError(message)
        if not isinstance(tags_raw, dict) or not isinstance(env_vars_raw, dict):
            message = "Malformed profile record: 'tags'/'env_vars' must be objects"
            raise ValueError(message)
        if not isinstance(firewall_rules_raw, list):
            message = "Malformed profile record: 'firewall_rules' must be a list"
            raise ValueError(message)
        storage = StorageConfig(**storage_raw)
        return InfrastructureProfile(
            name=str(raw["name"]),
            instance_type=str(raw["instance_type"]),
            region=str(raw["region"]),
            tags={str(k): str(v) for k, v in tags_raw.items()},
            firewall_rules=[str(item) for item in firewall_rules_raw],
            env_vars={str(k): str(v) for k, v in env_vars_raw.items()},
            storage=storage,
        )
