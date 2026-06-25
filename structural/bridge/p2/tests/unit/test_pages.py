"""Unit tests for the Abstraction hierarchy (Page subclasses).

Uses a fake renderer to verify the Bridge: pages delegate serialization
to whatever ContentRenderer they are given, without knowing its type.
"""

from __future__ import annotations

from renderer.domain.entities import (
    BlogPostData,
    PageContent,
    ProductData,
    UserProfileData,
)
from renderer.domain.interfaces import ContentRenderer
from renderer.domain.pages import BlogPostPage, ProductPage, UserProfilePage


class RecordingRenderer(ContentRenderer):
    """Test double that records the PageContent it was asked to render."""

    def __init__(self) -> None:
        self.received: PageContent | None = None

    @property
    def content_type(self) -> str:
        return "text/plain"

    def render_page(self, content: PageContent) -> str:
        self.received = content
        return f"rendered:{content.page_type}"


def test_product_page_delegates_to_renderer(sample_product: ProductData) -> None:
    renderer = RecordingRenderer()
    page = ProductPage(renderer, sample_product)

    result = page.render()

    assert result == "rendered:product"
    assert renderer.received is not None
    assert renderer.received.data["name"] == sample_product.name


def test_blog_post_page_delegates_to_renderer(sample_blog_post: BlogPostData) -> None:
    renderer = RecordingRenderer()
    page = BlogPostPage(renderer, sample_blog_post)

    result = page.render()

    assert result == "rendered:blog_post"
    assert renderer.received is not None
    assert renderer.received.data["slug"] == sample_blog_post.slug


def test_user_profile_page_delegates_to_renderer(
    sample_user_profile: UserProfileData,
) -> None:
    renderer = RecordingRenderer()
    page = UserProfilePage(renderer, sample_user_profile)

    result = page.render()

    assert result == "rendered:user_profile"
    assert renderer.received is not None
    assert renderer.received.title == f"Profile: {sample_user_profile.username}"
