"""Refined Abstractions — concrete page types.

Each page type knows WHAT data it represents and how to structure
a PageContent; rendering format is delegated to the injected renderer.
"""

from __future__ import annotations

from renderer.domain.entities import (
    BlogPostData,
    PageContent,
    ProductData,
    UserProfileData,
)
from renderer.domain.interfaces import ContentRenderer, Page


class ProductPage(Page):
    """Page that displays product details."""

    def __init__(self, renderer: ContentRenderer, product: ProductData) -> None:
        super().__init__(renderer)
        self._product = product

    def render(self) -> str:
        content = PageContent(
            title=self._product.name,
            page_type="product",
            data={
                "id": self._product.id,
                "name": self._product.name,
                "price": self._product.price,
                "description": self._product.description,
                "stock": self._product.stock,
                "category": self._product.category,
            },
            metadata={"schema": "product/v1"},
        )
        return self._renderer.render_page(content)


class BlogPostPage(Page):
    """Page that displays a blog article."""

    def __init__(self, renderer: ContentRenderer, post: BlogPostData) -> None:
        super().__init__(renderer)
        self._post = post

    def render(self) -> str:
        content = PageContent(
            title=self._post.title,
            page_type="blog_post",
            data={
                "slug": self._post.slug,
                "title": self._post.title,
                "author": self._post.author,
                "content": self._post.content,
                "tags": self._post.tags,
                "published_at": self._post.published_at,
            },
            metadata={"schema": "blog/v1"},
        )
        return self._renderer.render_page(content)


class UserProfilePage(Page):
    """Page that displays a user's public profile."""

    def __init__(self, renderer: ContentRenderer, profile: UserProfileData) -> None:
        super().__init__(renderer)
        self._profile = profile

    def render(self) -> str:
        content = PageContent(
            title=f"Profile: {self._profile.username}",
            page_type="user_profile",
            data={
                "user_id": self._profile.user_id,
                "username": self._profile.username,
                "email": self._profile.email,
                "bio": self._profile.bio,
                "join_date": self._profile.join_date,
                "post_count": self._profile.post_count,
            },
            metadata={"schema": "user/v1"},
        )
        return self._renderer.render_page(content)
