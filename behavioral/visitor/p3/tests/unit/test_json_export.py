"""Unit tests for JSONExportVisitor."""

from __future__ import annotations

import json

from content_export_visitor.application.structure import traverse
from content_export_visitor.domain.interfaces import (
    ArticleContent,
    ImageContent,
    VideoContent,
)
from content_export_visitor.infrastructure.visitors.json_export import (
    JSONExportVisitor,
)


def test_traverse_produces_one_entry_per_node() -> None:
    nodes = [
        ArticleContent(title="Hello", body="World"),
        ImageContent(url="http://x/y.png", caption="A pic"),
        VideoContent(url="http://x/v.mp4", duration_seconds=90),
    ]

    result = traverse(nodes, JSONExportVisitor())

    parsed = json.loads(result.content)
    assert len(parsed) == 3
    assert parsed[0] == {"type": "article", "title": "Hello", "body": "World"}
    assert parsed[2]["duration_seconds"] == 90


def test_get_file_extension() -> None:
    assert JSONExportVisitor().get_file_extension() == ".json"
