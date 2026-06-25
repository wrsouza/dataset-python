"""JSONExportVisitor: serialises every content node as a JSON array."""

from __future__ import annotations

import json

from content_export_visitor.domain.interfaces import (
    ArticleContent,
    ContentVisitor,
    ImageContent,
    VideoContent,
    VisitorResult,
)


class JSONExportVisitor(ContentVisitor):
    def __init__(self) -> None:
        self._items: list[dict[str, object]] = []

    def visit_article(self, node: ArticleContent) -> None:
        self._items.append({"type": "article", "title": node.title, "body": node.body})

    def visit_image(self, node: ImageContent) -> None:
        self._items.append({"type": "image", "url": node.url, "caption": node.caption})

    def visit_video(self, node: VideoContent) -> None:
        self._items.append(
            {
                "type": "video",
                "url": node.url,
                "duration_seconds": node.duration_seconds,
            }
        )

    def get_file_extension(self) -> str:
        return ".json"

    @property
    def result(self) -> VisitorResult:
        return VisitorResult(content=json.dumps(self._items, indent=2))
