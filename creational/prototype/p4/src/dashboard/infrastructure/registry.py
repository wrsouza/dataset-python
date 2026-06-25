"""JSON-persisted PrototypeRegistry for dashboard configs.

SRP: this class is only responsible for loading, saving, and cloning configs.
OCP: new dashboard types are supported by extending prototypes.py — no changes here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dashboard.domain.entities import TemplateNotFoundError
from dashboard.domain.interfaces import DashboardConfig, DashboardRegistry
from dashboard.infrastructure.prototypes import (
    BaseDashboardConfig,
    InventoryDashboardConfig,
    MarketingDashboardConfig,
    SalesDashboardConfig,
    deserialize_config,
)


class JsonDashboardRegistry(DashboardRegistry):
    """DashboardRegistry persisted as a JSON file.

    On construction, loads all templates from `registry_path` (if it exists).
    On register(), immediately persists to JSON.

    This way Streamlit reruns see the same state across sessions.
    """

    def __init__(self, registry_path: Path) -> None:
        self._path = registry_path
        self._templates: dict[str, BaseDashboardConfig] = {}
        self._load()

    # ── Persistence ────────────────────────────────────────────────────────────

    def _load(self) -> None:
        """Load templates from JSON file if it exists."""
        if not self._path.exists():
            return
        raw: dict[str, Any] = json.loads(self._path.read_text(encoding="utf-8"))
        for name, data in raw.items():
            self._templates[name] = deserialize_config(data)

    def _save(self) -> None:
        """Persist all templates to JSON."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {name: cfg.to_dict() for name, cfg in self._templates.items()}
        self._path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ── DashboardRegistry interface ────────────────────────────────────────────

    def register(self, name: str, config: DashboardConfig) -> None:
        """Register (or overwrite) a config template and persist."""
        if not isinstance(config, BaseDashboardConfig):
            raise TypeError(
                f"Expected BaseDashboardConfig, got {type(config).__name__}"
            )
        self._templates[name] = config
        self._save()

    def get(self, name: str) -> BaseDashboardConfig:
        """Retrieve a registered template by name."""
        if name not in self._templates:
            raise TemplateNotFoundError(name)
        return self._templates[name]

    def clone(self, name: str, overrides: dict[str, Any]) -> BaseDashboardConfig:
        """Clone a template and apply overrides.

        The original template is never mutated — copy.deepcopy inside clone()
        ensures a completely new object graph.
        """
        template = self.get(name)
        cloned = template.clone(overrides)
        if not isinstance(cloned, BaseDashboardConfig):
            raise TypeError("clone() must return a BaseDashboardConfig")
        return cloned

    def list_templates(self) -> list[str]:
        """Return all registered template names."""
        return list(self._templates.keys())


def build_default_registry(registry_path: Path) -> JsonDashboardRegistry:
    """Factory that builds a registry seeded with default templates.

    If the JSON file already exists (from a previous session), it loads
    existing templates and adds only the missing defaults.
    """
    registry = JsonDashboardRegistry(registry_path)

    if "vendas-brasil" not in registry.list_templates():
        registry.register(
            "vendas-brasil",
            SalesDashboardConfig(
                title="Vendas Brasil — 30 dias",
                date_range="last_30_days",
                metrics=["revenue", "orders", "avg_ticket"],
                revenue_target=500_000.0,
                currency="BRL",
            ),
        )

    if "estoque-geral" not in registry.list_templates():
        registry.register(
            "estoque-geral",
            InventoryDashboardConfig(
                title="Estoque Geral — Semanal",
                date_range="last_7_days",
                reorder_alert_threshold=15,
            ),
        )

    if "marketing-q4" not in registry.list_templates():
        registry.register(
            "marketing-q4",
            MarketingDashboardConfig(
                title="Marketing Q4 — Campanhas",
                date_range="last_90_days",
                campaigns=["black_friday", "natal", "ano_novo"],
                attribution_model="linear",
            ),
        )

    return registry
