"""Builds concrete ContentNode instances from plain dict payloads (HTTP JSON)."""

from __future__ import annotations

from typing import Any

from content_export_visitor.domain.exceptions import InvalidNodeTypeError
from content_export_visitor.domain.interfaces import (
    ArticleContent,
    ContentNode,
    ImageContent,
    VideoContent,
)


def build_node(payload: dict[str, Any]) -> ContentNode:
    node_type = payload.get("type", "")
    if node_type == "article":
        return ArticleContent(title=payload["title"], body=payload["body"])
    if node_type == "image":
        return ImageContent(url=payload["url"], caption=payload.get("caption", ""))
    if node_type == "video":
        return VideoContent(
            url=payload["url"], duration_seconds=payload.get("duration_seconds", 0)
        )
    raise InvalidNodeTypeError(node_type)


def build_nodes(payloads: list[dict[str, Any]]) -> list[ContentNode]:
    return [build_node(payload) for payload in payloads]
