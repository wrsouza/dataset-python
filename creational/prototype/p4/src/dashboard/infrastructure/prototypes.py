"""Concrete Prototype implementations for dashboard configurations.

Each class is a ConcretePrototype. copy.deepcopy ensures lists (metrics,
filters, chart_types) are independent in each clone.
"""

from __future__ import annotations

import copy
from typing import Any

from dashboard.domain.interfaces import DashboardConfig


class BaseDashboardConfig(DashboardConfig):
    """Base implementation shared by all concrete dashboard configs.

    Stores common fields: title, date_range, filters, chart_type,
    metrics, theme. Subclasses add domain-specific fields via _extra.
    """

    def __init__(
        self,
        title: str,
        dashboard_type: str,
        date_range: str,
        filters: list[str],
        chart_type: str,
        metrics: list[str],
        theme: str,
        extra: dict[str, Any] | None = None,
    ) -> None:
        self._title = title
        self._dashboard_type = dashboard_type
        self._date_range = date_range
        # Deep-copy mutable containers to ensure each instance is independent
        self._filters = list(filters)
        self._chart_type = chart_type
        self._metrics = list(metrics)
        self._theme = theme
        self._extra: dict[str, Any] = dict(extra or {})

    @property
    def title(self) -> str:
        return self._title

    @property
    def dashboard_type(self) -> str:
        return self._dashboard_type

    @property
    def date_range(self) -> str:
        return self._date_range

    @property
    def filters(self) -> list[str]:
        return list(self._filters)

    @property
    def chart_type(self) -> str:
        return self._chart_type

    @property
    def metrics(self) -> list[str]:
        return list(self._metrics)

    @property
    def theme(self) -> str:
        return self._theme

    @property
    def extra(self) -> dict[str, Any]:
        return dict(self._extra)

    def clone(self, overrides: dict[str, Any]) -> BaseDashboardConfig:
        """Deep clone and apply overrides.

        copy.deepcopy ensures nested lists (_filters, _metrics) and dicts
        (_extra) are brand-new objects in the clone.
        """
        cloned = copy.deepcopy(self)
        cloned._apply_overrides(overrides)
        return cloned

    def _apply_overrides(self, overrides: dict[str, Any]) -> None:
        """Apply override values to this (already cloned) instance."""
        if "title" in overrides:
            self._title = str(overrides["title"])
        if "date_range" in overrides:
            self._date_range = str(overrides["date_range"])
        if "filters" in overrides and isinstance(overrides["filters"], list):
            self._filters = list(overrides["filters"])
        if "chart_type" in overrides:
            self._chart_type = str(overrides["chart_type"])
        if "metrics" in overrides and isinstance(overrides["metrics"], list):
            self._metrics = list(overrides["metrics"])
        if "theme" in overrides:
            self._theme = str(overrides["theme"])
        # Extra fields are merged (not replaced), preserving subclass-specific data
        for key, value in overrides.items():
            if key not in {
                "title",
                "date_range",
                "filters",
                "chart_type",
                "metrics",
                "theme",
            }:
                self._extra[key] = value

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self._title,
            "dashboard_type": self._dashboard_type,
            "date_range": self._date_range,
            "filters": list(self._filters),
            "chart_type": self._chart_type,
            "metrics": list(self._metrics),
            "theme": self._theme,
            "extra": dict(self._extra),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseDashboardConfig:
        """Reconstruct from a serialized dictionary."""
        return cls(
            title=data["title"],
            dashboard_type=data["dashboard_type"],
            date_range=data.get("date_range", "last_30_days"),
            filters=data.get("filters", []),
            chart_type=data.get("chart_type", "bar"),
            metrics=data.get("metrics", []),
            theme=data.get("theme", "light"),
            extra=data.get("extra", {}),
        )


class SalesDashboardConfig(BaseDashboardConfig):
    """ConcretePrototype for sales dashboards.

    Adds sales-specific fields: revenue_target, currency, sales_channels.
    """

    def __init__(
        self,
        title: str = "Vendas — Dashboard",
        date_range: str = "last_30_days",
        filters: list[str] | None = None,
        chart_type: str = "bar",
        metrics: list[str] | None = None,
        theme: str = "light",
        revenue_target: float = 100_000.0,
        currency: str = "BRL",
        sales_channels: list[str] | None = None,
    ) -> None:
        super().__init__(
            title=title,
            dashboard_type="sales",
            date_range=date_range,
            filters=filters or ["region", "product_line"],
            chart_type=chart_type,
            metrics=metrics or ["revenue", "orders", "avg_ticket"],
            theme=theme,
            extra={
                "revenue_target": revenue_target,
                "currency": currency,
                "sales_channels": list(sales_channels or ["online", "retail"]),
            },
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SalesDashboardConfig:
        extra = data.get("extra", {})
        return cls(
            title=data["title"],
            date_range=data.get("date_range", "last_30_days"),
            filters=data.get("filters", []),
            chart_type=data.get("chart_type", "bar"),
            metrics=data.get("metrics", []),
            theme=data.get("theme", "light"),
            revenue_target=float(extra.get("revenue_target", 100_000.0)),
            currency=str(extra.get("currency", "BRL")),
            sales_channels=list(extra.get("sales_channels", ["online", "retail"])),
        )


class InventoryDashboardConfig(BaseDashboardConfig):
    """ConcretePrototype for inventory dashboards.

    Adds inventory-specific fields: warehouse_ids, reorder_alert_threshold.
    """

    def __init__(
        self,
        title: str = "Estoque — Dashboard",
        date_range: str = "last_7_days",
        filters: list[str] | None = None,
        chart_type: str = "table",
        metrics: list[str] | None = None,
        theme: str = "dark",
        warehouse_ids: list[str] | None = None,
        reorder_alert_threshold: int = 20,
    ) -> None:
        super().__init__(
            title=title,
            dashboard_type="inventory",
            date_range=date_range,
            filters=filters or ["category", "supplier"],
            chart_type=chart_type,
            metrics=metrics or ["stock_level", "turnover_rate", "reorder_count"],
            theme=theme,
            extra={
                "warehouse_ids": list(warehouse_ids or ["WH-01", "WH-02"]),
                "reorder_alert_threshold": reorder_alert_threshold,
            },
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InventoryDashboardConfig:
        extra = data.get("extra", {})
        return cls(
            title=data["title"],
            date_range=data.get("date_range", "last_7_days"),
            filters=data.get("filters", []),
            chart_type=data.get("chart_type", "table"),
            metrics=data.get("metrics", []),
            theme=data.get("theme", "dark"),
            warehouse_ids=list(extra.get("warehouse_ids", ["WH-01"])),
            reorder_alert_threshold=int(extra.get("reorder_alert_threshold", 20)),
        )


class MarketingDashboardConfig(BaseDashboardConfig):
    """ConcretePrototype for marketing campaign dashboards.

    Adds marketing-specific fields: campaigns, attribution_model.
    """

    def __init__(
        self,
        title: str = "Marketing — Dashboard",
        date_range: str = "last_90_days",
        filters: list[str] | None = None,
        chart_type: str = "line",
        metrics: list[str] | None = None,
        theme: str = "light",
        campaigns: list[str] | None = None,
        attribution_model: str = "last_click",
    ) -> None:
        super().__init__(
            title=title,
            dashboard_type="marketing",
            date_range=date_range,
            filters=filters or ["channel", "campaign"],
            chart_type=chart_type,
            metrics=metrics or ["impressions", "clicks", "conversions", "cac"],
            theme=theme,
            extra={
                "campaigns": list(campaigns or ["summer_sale", "black_friday"]),
                "attribution_model": attribution_model,
            },
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MarketingDashboardConfig:
        extra = data.get("extra", {})
        return cls(
            title=data["title"],
            date_range=data.get("date_range", "last_90_days"),
            filters=data.get("filters", []),
            chart_type=data.get("chart_type", "line"),
            metrics=data.get("metrics", []),
            theme=data.get("theme", "light"),
            campaigns=list(extra.get("campaigns", [])),
            attribution_model=str(extra.get("attribution_model", "last_click")),
        )


# Registry of from_dict deserializers — OCP: add new type here, nowhere else
_DESERIALIZERS: dict[str, type[BaseDashboardConfig]] = {
    "sales": SalesDashboardConfig,
    "inventory": InventoryDashboardConfig,
    "marketing": MarketingDashboardConfig,
}


def deserialize_config(data: dict[str, Any]) -> BaseDashboardConfig:
    """Deserialize a config dict to the correct concrete type.

    Reads `dashboard_type` to dispatch to the right class.
    OCP: adding MarketingDashboardConfig required adding one entry to _DESERIALIZERS.
    """
    dashboard_type = data.get("dashboard_type", "sales")
    cls = _DESERIALIZERS.get(dashboard_type, BaseDashboardConfig)
    return cls.from_dict(data)
