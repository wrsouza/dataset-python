"""MarkdownExportVisitor: renders every content node as a Markdown section."""

from __future__ import annotations

from content_export_visitor.domain.interfaces import (
    ArticleContent,
    ContentVisitor,
    ImageContent,
    VideoContent,
    VisitorResult,
)


class MarkdownExportVisitor(ContentVisitor):
    def __init__(self) -> None:
        self._sections: list[str] = []

    def visit_article(self, node: ArticleContent) -> None:
        self._sections.append(f"## {node.title}\n\n{node.body}")

    def visit_image(self, node: ImageContent) -> None:
        self._sections.append(f"![{node.caption}]({node.url})")

    def visit_video(self, node: VideoContent) -> None:
        minutes, seconds = divmod(node.duration_seconds, 60)
        self._sections.append(f"[Video]({node.url}) — {minutes}m{seconds:02d}s")

    def get_file_extension(self) -> str:
        return ".md"

    @property
    def result(self) -> VisitorResult:
        return VisitorResult(content="\n\n".join(self._sections))
