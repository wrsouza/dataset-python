"""Unit tests for the visitor registry and node factory."""

from __future__ import annotations

import pytest

from content_export_visitor.application.node_factory import build_node, build_nodes
from content_export_visitor.domain.exceptions import (
    InvalidFormatError,
    InvalidNodeTypeError,
)
from content_export_visitor.domain.interfaces import ArticleContent, ImageContent
from content_export_visitor.infrastructure.visitors.json_export import (
    JSONExportVisitor,
)
from content_export_visitor.infrastructure.visitors.registry import (
    get_visitor,
    list_format_names,
)


def test_get_visitor_resolves_json() -> None:
    assert isinstance(get_visitor("json"), JSONExportVisitor)


def test_get_visitor_is_case_insensitive() -> None:
    assert get_visitor("MARKDOWN").get_file_extension() == ".md"


def test_get_visitor_raises_for_unknown_format() -> None:
    with pytest.raises(InvalidFormatError):
        get_visitor("pdf")


def test_list_format_names() -> None:
    assert list_format_names() == ["json", "markdown"]


def test_build_node_article() -> None:
    node = build_node({"type": "article", "title": "A", "body": "B"})

    assert isinstance(node, ArticleContent)


def test_build_node_image_defaults_caption() -> None:
    node = build_node({"type": "image", "url": "http://x"})

    assert isinstance(node, ImageContent)
    assert node.caption == ""


def test_build_node_raises_for_unknown_type() -> None:
    with pytest.raises(InvalidNodeTypeError):
        build_node({"type": "unknown"})


def test_build_nodes_builds_a_list() -> None:
    nodes = build_nodes(
        [{"type": "article", "title": "A", "body": "B"}, {"type": "image", "url": "x"}]
    )

    assert len(nodes) == 2
