"""Unit tests for JsonDashboardRegistry — register/get/clone/list."""

from __future__ import annotations

from pathlib import Path

import pytest

from dashboard.domain.entities import TemplateNotFoundError
from dashboard.infrastructure.prototypes import SalesDashboardConfig
from dashboard.infrastructure.registry import (
    JsonDashboardRegistry,
    build_default_registry,
)


@pytest.fixture
def registry_path(tmp_path: Path) -> Path:
    return tmp_path / "registry.json"


class TestJsonDashboardRegistry:
    def test_register_and_get(self, registry_path: Path) -> None:
        registry = JsonDashboardRegistry(registry_path)
        registry.register("vendas", SalesDashboardConfig(title="Vendas"))
        template = registry.get("vendas")
        assert template.title == "Vendas"

    def test_get_unknown_template_raises(self, registry_path: Path) -> None:
        registry = JsonDashboardRegistry(registry_path)
        with pytest.raises(TemplateNotFoundError):
            registry.get("inexistente")

    def test_register_rejects_wrong_type(self, registry_path: Path) -> None:
        registry = JsonDashboardRegistry(registry_path)
        with pytest.raises(TypeError):
            registry.register("bad", object())  # type: ignore[arg-type]

    def test_register_persists_to_disk(self, registry_path: Path) -> None:
        registry = JsonDashboardRegistry(registry_path)
        registry.register("vendas", SalesDashboardConfig(title="Vendas"))
        assert registry_path.exists()

    def test_reload_from_disk_restores_templates(self, registry_path: Path) -> None:
        first = JsonDashboardRegistry(registry_path)
        first.register("vendas", SalesDashboardConfig(title="Vendas"))

        second = JsonDashboardRegistry(registry_path)
        assert "vendas" in second.list_templates()
        assert second.get("vendas").title == "Vendas"

    def test_clone_creates_independent_copy(self, registry_path: Path) -> None:
        registry = JsonDashboardRegistry(registry_path)
        registry.register("vendas", SalesDashboardConfig(title="Vendas"))
        clone1 = registry.clone("vendas", {"title": "Clone A"})
        clone2 = registry.clone("vendas", {"title": "Clone B"})
        assert clone1.title != clone2.title

    def test_clone_does_not_modify_original(self, registry_path: Path) -> None:
        registry = JsonDashboardRegistry(registry_path)
        registry.register("vendas", SalesDashboardConfig(title="Vendas"))
        registry.clone("vendas", {"title": "Modificado"})
        assert registry.get("vendas").title == "Vendas"

    def test_list_templates(self, registry_path: Path) -> None:
        registry = JsonDashboardRegistry(registry_path)
        registry.register("vendas", SalesDashboardConfig())
        assert registry.list_templates() == ["vendas"]


class TestBuildDefaultRegistry:
    def test_seeds_default_templates(self, registry_path: Path) -> None:
        registry = build_default_registry(registry_path)
        templates = registry.list_templates()
        assert "vendas-brasil" in templates
        assert "estoque-geral" in templates
        assert "marketing-q4" in templates

    def test_does_not_duplicate_on_second_call(self, registry_path: Path) -> None:
        build_default_registry(registry_path)
        registry = build_default_registry(registry_path)
        assert registry.list_templates().count("vendas-brasil") == 1
