"""Unit tests for concrete dashboard prototypes — deep vs shallow copy."""

from __future__ import annotations

import copy

from dashboard.infrastructure.prototypes import (
    BaseDashboardConfig,
    InventoryDashboardConfig,
    MarketingDashboardConfig,
    SalesDashboardConfig,
    deserialize_config,
)


class TestSalesDashboardConfig:
    def test_default_fields(self) -> None:
        config = SalesDashboardConfig()
        assert config.dashboard_type == "sales"
        assert "revenue" in config.metrics

    def test_clone_returns_independent_instance(self) -> None:
        original = SalesDashboardConfig()
        cloned = original.clone({})
        assert cloned is not original

    def test_clone_deep_copies_metrics_list(self) -> None:
        original = SalesDashboardConfig(metrics=["revenue", "orders"])
        cloned = original.clone({"metrics": ["new_metric"]})
        assert cloned.metrics == ["new_metric"]
        assert original.metrics == ["revenue", "orders"]

    def test_clone_deep_copies_extra_dict(self) -> None:
        original = SalesDashboardConfig(sales_channels=["online"])
        cloned = original.clone({"sales_channels": ["retail", "wholesale"]})
        assert cloned.extra["sales_channels"] == ["retail", "wholesale"]
        assert original.extra["sales_channels"] == ["online"]

    def test_mutating_cloned_filters_does_not_affect_original(self) -> None:
        original = SalesDashboardConfig(filters=["region"])
        cloned = original.clone({})
        # Simulate external mutation attempt on the clone's nested list
        cloned_filters = cloned.filters
        cloned_filters.append("mutated")
        assert original.filters == ["region"]
        assert "mutated" not in cloned.filters

    def test_to_dict_and_from_dict_roundtrip(self) -> None:
        original = SalesDashboardConfig(title="X", revenue_target=10.0)
        data = original.to_dict()
        rebuilt = SalesDashboardConfig.from_dict(data)
        assert rebuilt.title == "X"
        assert rebuilt.extra["revenue_target"] == 10.0

    def test_apply_overrides_title_and_theme(self) -> None:
        original = SalesDashboardConfig()
        cloned = original.clone({"title": "Novo Título", "theme": "dark"})
        assert cloned.title == "Novo Título"
        assert cloned.theme == "dark"
        assert original.title != "Novo Título"


class TestInventoryDashboardConfig:
    def test_default_fields(self) -> None:
        config = InventoryDashboardConfig()
        assert config.dashboard_type == "inventory"
        assert config.theme == "dark"

    def test_clone_independent_warehouse_ids(self) -> None:
        original = InventoryDashboardConfig(warehouse_ids=["WH-01"])
        cloned = original.clone({"warehouse_ids": ["WH-99"]})
        assert cloned.extra["warehouse_ids"] == ["WH-99"]
        assert original.extra["warehouse_ids"] == ["WH-01"]

    def test_from_dict_roundtrip(self) -> None:
        original = InventoryDashboardConfig(reorder_alert_threshold=42)
        rebuilt = InventoryDashboardConfig.from_dict(original.to_dict())
        assert rebuilt.extra["reorder_alert_threshold"] == 42


class TestMarketingDashboardConfig:
    def test_default_fields(self) -> None:
        config = MarketingDashboardConfig()
        assert config.dashboard_type == "marketing"
        assert "impressions" in config.metrics

    def test_clone_independent_campaigns(self) -> None:
        original = MarketingDashboardConfig(campaigns=["black_friday"])
        cloned = original.clone({"campaigns": ["natal"]})
        assert cloned.extra["campaigns"] == ["natal"]
        assert original.extra["campaigns"] == ["black_friday"]

    def test_from_dict_roundtrip(self) -> None:
        original = MarketingDashboardConfig(attribution_model="linear")
        rebuilt = MarketingDashboardConfig.from_dict(original.to_dict())
        assert rebuilt.extra["attribution_model"] == "linear"


class TestDeserializeConfig:
    def test_deserialize_sales(self) -> None:
        data = SalesDashboardConfig().to_dict()
        result = deserialize_config(data)
        assert isinstance(result, SalesDashboardConfig)

    def test_deserialize_inventory(self) -> None:
        data = InventoryDashboardConfig().to_dict()
        result = deserialize_config(data)
        assert isinstance(result, InventoryDashboardConfig)

    def test_deserialize_marketing(self) -> None:
        data = MarketingDashboardConfig().to_dict()
        result = deserialize_config(data)
        assert isinstance(result, MarketingDashboardConfig)

    def test_deserialize_unknown_type_falls_back_to_base(self) -> None:
        data = SalesDashboardConfig().to_dict()
        data["dashboard_type"] = "unknown"
        result = deserialize_config(data)
        # Unknown types fall back to BaseDashboardConfig (not a registered subclass)
        assert type(result) is BaseDashboardConfig


class TestDeepCopyVsShallowCopy:
    """Explicitly proves why clone() must use copy.deepcopy, not copy.copy."""

    def test_deepcopy_isolates_nested_list(self) -> None:
        original = SalesDashboardConfig(metrics=["revenue"])
        deep_copy = copy.deepcopy(original)
        deep_copy._metrics.append("mutated")  # noqa: SLF001
        assert original.metrics == ["revenue"]

    def test_shallow_copy_shares_nested_list(self) -> None:
        original = SalesDashboardConfig(metrics=["revenue"])
        shallow = copy.copy(original)
        shallow._metrics.append("mutated")  # noqa: SLF001
        # Shallow copy shares the same list object — original IS affected.
        assert "mutated" in original.metrics
