"""Unit tests for Leaf widgets (MetricCard, TextBlock, ChartWidget)."""

from __future__ import annotations

from src.dashboard.domain.entities import ChartData, MetricCardData, TextBlockData
from src.dashboard.infrastructure.widgets import ChartWidget, MetricCard, TextBlock


class TestMetricCard:
    def test_render_returns_expected_shape(self) -> None:
        card = MetricCard(
            "revenue_card", MetricCardData(label="Receita", value="R$ 100", delta="+5%")
        )
        rendered = card.render()
        assert rendered == {
            "type": "metric_card",
            "name": "revenue_card",
            "label": "Receita",
            "value": "R$ 100",
            "delta": "+5%",
        }

    def test_name_and_component_type(self) -> None:
        card = MetricCard("orders_card", MetricCardData(label="Pedidos", value="10"))
        assert card.name == "orders_card"
        assert card.component_type == "metric_card"

    def test_leaf_counts_as_one_widget(self) -> None:
        card = MetricCard("card", MetricCardData(label="X", value="1"))
        assert card.count_widgets() == 1

    def test_leaf_depth_is_one(self) -> None:
        card = MetricCard("card", MetricCardData(label="X", value="1"))
        assert card.depth() == 1


class TestTextBlock:
    def test_render_returns_expected_shape(self) -> None:
        block = TextBlock("note", TextBlockData(content="Olá", markdown=False))
        assert block.render() == {
            "type": "text_block",
            "name": "note",
            "content": "Olá",
            "markdown": False,
        }

    def test_leaf_counts_and_depth(self) -> None:
        block = TextBlock("note", TextBlockData(content="Olá"))
        assert block.count_widgets() == 1
        assert block.depth() == 1


class TestChartWidget:
    def test_render_returns_expected_shape(self) -> None:
        chart = ChartWidget(
            "revenue_chart",
            ChartData(
                chart_type="line", series={"a": [1.0, 2.0]}, x_labels=["Jan", "Fev"]
            ),
        )
        assert chart.render() == {
            "type": "chart",
            "name": "revenue_chart",
            "chart_type": "line",
            "series": {"a": [1.0, 2.0]},
            "x_labels": ["Jan", "Fev"],
        }

    def test_leaf_counts_and_depth(self) -> None:
        chart = ChartWidget("c", ChartData(chart_type="bar"))
        assert chart.count_widgets() == 1
        assert chart.depth() == 1
