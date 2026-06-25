"""Unit tests for the Implementation hierarchy (ContentRenderer)."""

from __future__ import annotations

import json

from renderer.domain.entities import PageContent
from renderer.infrastructure.implementations import (
    HTMLRenderer,
    JSONRenderer,
    XMLRenderer,
)


def test_json_renderer_content_type() -> None:
    renderer = JSONRenderer()
    assert renderer.content_type == "application/json"


def test_json_renderer_serializes_page_content() -> None:
    renderer = JSONRenderer()
    content = PageContent(
        title="Test", page_type="generic", data={"a": 1}, metadata={"schema": "x"}
    )

    result = json.loads(renderer.render_page(content))

    assert result["title"] == "Test"
    assert result["data"] == {"a": 1}
    assert result["metadata"] == {"schema": "x"}


def test_xml_renderer_content_type() -> None:
    renderer = XMLRenderer()
    assert renderer.content_type == "application/xml"


def test_xml_renderer_serializes_nested_and_list_data() -> None:
    renderer = XMLRenderer()
    content = PageContent(
        title="Test",
        page_type="blog_post",
        data={"tags": ["a", "b"], "nested": {"k": "v"}},
    )

    result = renderer.render_page(content)

    assert "<title>Test</title>" in result
    assert "<item>a</item>" in result
    assert "<item>b</item>" in result
    assert "<k>v</k>" in result


def test_html_renderer_content_type() -> None:
    renderer = HTMLRenderer()
    assert renderer.content_type == "text/html; charset=utf-8"


def test_html_renderer_uses_specific_template() -> None:
    renderer = HTMLRenderer()
    content = PageContent(
        title="Mouse",
        page_type="product",
        data={
            "name": "Mouse",
            "category": "Peripherals",
            "price": 59.9,
            "stock": 5,
            "description": "A mouse.",
        },
    )

    result = renderer.render_page(content)

    assert "Mouse" in result
    assert "Peripherals" in result


def test_html_renderer_falls_back_to_generic_template() -> None:
    renderer = HTMLRenderer()
    content = PageContent(
        title="Unknown", page_type="does_not_exist", data={"foo": "bar"}
    )

    result = renderer.render_page(content)

    assert "Unknown" in result
    assert "foo" in result
