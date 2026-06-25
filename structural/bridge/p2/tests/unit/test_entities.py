"""Unit tests for domain entities."""

from __future__ import annotations

from renderer.domain.entities import PageContent, ProductData


def test_page_content_defaults_are_independent() -> None:
    first = PageContent(title="A", page_type="generic")
    second = PageContent(title="B", page_type="generic")

    first.data["x"] = 1

    assert "x" not in second.data


def test_product_data_is_frozen(sample_product: ProductData) -> None:
    assert sample_product.name == "Wireless Mouse"
    assert sample_product.price == 59.90
