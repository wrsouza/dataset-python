"""Domain entities for the Renderer domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PageContent:
    """Neutral representation of page data; renderers serialize it."""

    title: str
    page_type: str
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProductData:
    id: str
    name: str
    price: float
    description: str
    stock: int
    category: str


@dataclass(frozen=True)
class BlogPostData:
    slug: str
    title: str
    author: str
    content: str
    tags: list[str]
    published_at: str


@dataclass(frozen=True)
class UserProfileData:
    user_id: str
    username: str
    email: str
    bio: str
    join_date: str
    post_count: int
