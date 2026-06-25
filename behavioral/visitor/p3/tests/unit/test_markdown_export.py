"""Unit tests for MarkdownExportVisitor."""

from __future__ import annotations

from content_export_visitor.application.structure import traverse
from content_export_visitor.domain.interfaces import (
    ArticleContent,
    ImageContent,
    VideoContent,
)
from content_export_visitor.infrastructure.visitors.markdown_export import (
    MarkdownExportVisitor,
)


def test_traverse_renders_markdown_sections() -> None:
    nodes = [
        ArticleContent(title="Hello", body="World"),
        ImageContent(url="http://x/y.png", caption="A pic"),
        VideoContent(url="http://x/v.mp4", duration_seconds=90),
    ]

    result = traverse(nodes, MarkdownExportVisitor())

    assert "## Hello" in result.content
    assert "![A pic](http://x/y.png)" in result.content
    assert "1m30s" in result.content


def test_get_file_extension() -> None:
    assert MarkdownExportVisitor().get_file_extension() == ".md"
