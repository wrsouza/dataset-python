"""Domain interfaces: ContentVisitor ABC and ContentNode ABC.

Visitor pattern separates the export algorithm (JSON, Markdown, ...)
from the content structure (article/image/video nodes), enabling new
export formats without modifying the node classes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class VisitorResult:
    """Aggregated result returned after a visitor traverses all content nodes."""

    content: str = ""


class ContentVisitor(ABC):
    """Abstract Visitor — one visit_X method per concrete ContentNode type.

    Adding a new export format means creating a new ContentVisitor
    subclass; existing ContentNode subclasses are never modified (OCP).
    """

    @abstractmethod
    def visit_article(self, node: ArticleContent) -> None:
        """Process an article (title + body text) node."""

    @abstractmethod
    def visit_image(self, node: ImageContent) -> None:
        """Process an image (url + caption) node."""

    @abstractmethod
    def visit_video(self, node: VideoContent) -> None:
        """Process a video (url + duration) node."""

    @abstractmethod
    def get_file_extension(self) -> str:
        """Return the file extension this visitor's output uses."""

    @property
    def result(self) -> VisitorResult:
        """Return the accumulated result after traversal."""
        return VisitorResult()


class ContentNode(ABC):
    """Abstract Element — every content node exposes accept(visitor).

    Double-dispatch: the node calls the specific visit_X on the visitor,
    so the visitor always knows the concrete type without isinstance checks.
    """

    @abstractmethod
    def accept(self, visitor: ContentVisitor) -> None:
        """Accept a visitor and call the appropriate visit_X method."""


@dataclass
class ArticleContent(ContentNode):
    title: str
    body: str

    def accept(self, visitor: ContentVisitor) -> None:
        visitor.visit_article(self)


@dataclass
class ImageContent(ContentNode):
    url: str
    caption: str = ""

    def accept(self, visitor: ContentVisitor) -> None:
        visitor.visit_image(self)


@dataclass
class VideoContent(ContentNode):
    url: str
    duration_seconds: int = field(default=0)

    def accept(self, visitor: ContentVisitor) -> None:
        visitor.visit_video(self)


__all__ = [
    "ContentVisitor",
    "ContentNode",
    "VisitorResult",
    "ArticleContent",
    "ImageContent",
    "VideoContent",
]
