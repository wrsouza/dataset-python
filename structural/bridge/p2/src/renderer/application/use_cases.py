"""Use cases — orchestrate Page (abstraction) + ContentRenderer (implementation).

This is where the Bridge actually "bridges": callers choose a page type
and a renderer independently, and the use case wires them together
without either hierarchy knowing about the other's concrete classes.
"""

from __future__ import annotations

from renderer.domain.entities import BlogPostData, ProductData, UserProfileData
from renderer.domain.interfaces import ContentRenderer
from renderer.domain.pages import BlogPostPage, ProductPage, UserProfilePage

# In-memory catalogs standing in for a real datastore. Keeping persistence
# out of this layer keeps the use case focused on rendering orchestration.
_PRODUCTS: dict[str, ProductData] = {
    "p-100": ProductData(
        id="p-100",
        name="Mechanical Keyboard",
        price=149.90,
        description="Hot-swappable mechanical keyboard with RGB backlight.",
        stock=42,
        category="Peripherals",
    ),
}

_BLOG_POSTS: dict[str, BlogPostData] = {
    "bridge-pattern-explained": BlogPostData(
        slug="bridge-pattern-explained",
        title="The Bridge Pattern Explained",
        author="Jane Doe",
        content="The Bridge pattern decouples an abstraction from its implementation.",
        tags=["design-patterns", "python", "architecture"],
        published_at="2026-05-01",
    ),
}

_USER_PROFILES: dict[str, UserProfileData] = {
    "u-1": UserProfileData(
        user_id="u-1",
        username="janedoe",
        email="jane@example.com",
        bio="Backend engineer interested in design patterns.",
        join_date="2024-02-10",
        post_count=12,
    ),
}


class PageNotFoundError(Exception):
    """Raised when the requested page identifier does not exist."""


class RenderPageUseCase:
    """Resolves a page's data and renders it with the requested renderer.

    Dependency Inversion: this use case depends only on the ``Page``
    and ``ContentRenderer`` abstractions; concrete renderers are injected
    by the caller (the Flask route), never instantiated here.
    """

    def render_product(self, product_id: str, renderer: ContentRenderer) -> str:
        """Render a product page through the given renderer."""
        product = _PRODUCTS.get(product_id)
        if product is None:
            raise PageNotFoundError(f"Product '{product_id}' not found")
        page = ProductPage(renderer, product)
        return page.render()

    def render_blog_post(self, slug: str, renderer: ContentRenderer) -> str:
        """Render a blog post page through the given renderer."""
        post = _BLOG_POSTS.get(slug)
        if post is None:
            raise PageNotFoundError(f"Blog post '{slug}' not found")
        page = BlogPostPage(renderer, post)
        return page.render()

    def render_user_profile(self, user_id: str, renderer: ContentRenderer) -> str:
        """Render a user profile page through the given renderer."""
        profile = _USER_PROFILES.get(user_id)
        if profile is None:
            raise PageNotFoundError(f"User profile '{user_id}' not found")
        page = UserProfilePage(renderer, profile)
        return page.render()
