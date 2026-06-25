"""Bridge pattern interfaces — Renderer domain.

Two independent hierarchies:
- Abstraction: Page (what content to show)
- Implementation: ContentRenderer (what format to output)
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from renderer.domain.entities import PageContent


class ContentRenderer(ABC):
    """Implementation hierarchy — output format.

    Concrete renderers know HOW to serialize PageContent
    (HTML, JSON, XML). They are unaware of page types.
    """

    @abstractmethod
    def render_page(self, content: PageContent) -> str:
        """Serialize page content into the target format.

        Args:
            content: Structured page content.

        Returns:
            Serialized string in the renderer's format.
        """

    @property
    @abstractmethod
    def content_type(self) -> str:
        """MIME type produced by this renderer."""


class Page(ABC):
    """Abstraction hierarchy — page/content type.

    Subclasses know WHAT data to fetch and how to build PageContent;
    they delegate serialization to the injected renderer (bridge).
    """

    def __init__(self, renderer: ContentRenderer) -> None:
        # Bridge: composition over inheritance for output format.
        self._renderer = renderer

    @abstractmethod
    def render(self) -> str:
        """Build page-specific content and forward to renderer."""
