"""Concrete FlagLoader implementations.

OCP: each loader is a self-contained extension — JsonFlagLoader handles
local files, SsmFlagLoader (stub) would handle AWS SSM Parameter Store.
No existing code changes when a new loader is added.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from feature_flags.domain.entities import FlagConfig, FlagType
from feature_flags.domain.interfaces import FlagLoadError


class JsonFlagLoader:
    """Loads feature flags from a local JSON file.

    Simulates AWS AppConfig / SSM by reading a flags.json file that could
    be injected via ConfigMap in Kubernetes or mounted from S3.

    Expected format:
        {
          "flag_name": {
            "enabled": true,
            "rollout_percentage": 50,
            "allowlist": ["user_1", "user_2"]
          }
        }
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def load(self) -> dict[str, FlagConfig]:
        """Parse flags.json and return a dict of FlagConfig objects.

        Raises:
            FlagLoadError: when the file is missing or contains invalid JSON.
        """
        if not self._path.exists():
            raise FlagLoadError(f"flags file not found: {self._path}")

        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise FlagLoadError(f"invalid JSON in {self._path}: {exc}") from exc

        return {name: self._parse_flag(name, cfg) for name, cfg in raw.items()}

    def _parse_flag(self, name: str, cfg: dict) -> FlagConfig:  # type: ignore[type-arg]
        """Convert a raw dict to a FlagConfig with type inference."""
        rollout = int(cfg.get("rollout_percentage", 0))
        allowlist: list[str] = cfg.get("allowlist", [])

        # Infer flag type from which fields are populated.
        if allowlist:
            flag_type = FlagType.ALLOWLIST
        elif rollout > 0:
            flag_type = FlagType.PERCENTAGE
        else:
            flag_type = FlagType.BOOLEAN

        return FlagConfig(
            name=name,
            enabled=bool(cfg.get("enabled", False)),
            rollout_percentage=rollout,
            allowlist=allowlist,
            flag_type=flag_type,
        )


class EnvFlagLoader:
    """Loads flags from environment variables — useful in CI or Docker.

    Each flag is an env var: FEATURE_<FLAG_NAME>=true|false
    """

    PREFIX = "FEATURE_"

    def load(self) -> dict[str, FlagConfig]:
        flags: dict[str, FlagConfig] = {}
        for key, value in os.environ.items():
            if key.startswith(self.PREFIX):
                name = key[len(self.PREFIX):].lower()
                flags[name] = FlagConfig(
                    name=name,
                    enabled=value.lower() in {"1", "true", "yes"},
                )
        return flags
