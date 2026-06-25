"""Integration test: full workflow registry -> clone -> edit -> independence."""

from __future__ import annotations

from pathlib import Path

from dashboard.application.use_cases import (
    CloneDashboardUseCase,
    EditClonedDashboardUseCase,
    GetDashboardTemplateUseCase,
    ListDashboardTemplatesUseCase,
    RegisterDashboardTemplateUseCase,
)
from dashboard.infrastructure.prototypes import SalesDashboardConfig
from dashboard.infrastructure.registry import JsonDashboardRegistry


def test_full_clone_edit_independence_workflow(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.json"
    registry = JsonDashboardRegistry(registry_path)

    register_use_case = RegisterDashboardTemplateUseCase(registry)
    list_use_case = ListDashboardTemplatesUseCase(registry)
    get_use_case = GetDashboardTemplateUseCase(registry)
    clone_use_case = CloneDashboardUseCase(registry)
    edit_use_case = EditClonedDashboardUseCase()

    register_use_case.execute(
        "vendas-brasil",
        SalesDashboardConfig(
            title="Vendas Brasil",
            metrics=["revenue", "orders"],
            sales_channels=["online", "retail"],
        ),
    )

    assert "vendas-brasil" in list_use_case.execute()

    cloned = clone_use_case.execute("vendas-brasil", overrides={})
    edited = edit_use_case.execute(
        cloned,
        {"title": "Vendas Brasil — Q1", "metrics": ["revenue"]},
    )

    original = get_use_case.execute("vendas-brasil")

    assert edited.title == "Vendas Brasil — Q1"
    assert edited.metrics == ["revenue"]
    assert original.title == "Vendas Brasil"
    assert original.metrics == ["revenue", "orders"]


def test_cloning_twice_from_same_template_yields_independent_objects(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "registry.json"
    registry = JsonDashboardRegistry(registry_path)
    register_use_case = RegisterDashboardTemplateUseCase(registry)
    clone_use_case = CloneDashboardUseCase(registry)

    register_use_case.execute("vendas-brasil", SalesDashboardConfig())

    clone_a = clone_use_case.execute("vendas-brasil", {"title": "A"})
    clone_b = clone_use_case.execute("vendas-brasil", {"title": "B"})

    assert clone_a.title == "A"
    assert clone_b.title == "B"
    assert clone_a is not clone_b
