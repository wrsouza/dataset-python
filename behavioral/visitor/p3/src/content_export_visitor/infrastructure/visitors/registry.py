"""Visitor registry — maps format names to ContentVisitor factories."""

from __future__ import annotations

from content_export_visitor.domain.exceptions import InvalidFormatError
from content_export_visitor.domain.interfaces import ContentVisitor
from content_export_visitor.infrastructure.visitors.json_export import (
    JSONExportVisitor,
)
from content_export_visitor.infrastructure.visitors.markdown_export import (
    MarkdownExportVisitor,
)

_VISITOR_FACTORIES: dict[str, type[ContentVisitor]] = {
    "json": JSONExportVisitor,
    "markdown": MarkdownExportVisitor,
}


def get_visitor(name: str) -> ContentVisitor:
    factory = _VISITOR_FACTORIES.get(name.lower())
    if factory is None:
        raise InvalidFormatError(name)
    return factory()


def list_format_names() -> list[str]:
    return sorted(_VISITOR_FACTORIES)
