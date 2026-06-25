"""Shared fixtures for Renderer Bridge tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from flask.testing import FlaskClient

from renderer.app import create_app
from renderer.domain.entities import BlogPostData, ProductData, UserProfileData


@pytest.fixture
def sample_product() -> ProductData:
    return ProductData(
        id="p-1",
        name="Wireless Mouse",
        price=59.90,
        description="Ergonomic wireless mouse.",
        stock=10,
        category="Peripherals",
    )


@pytest.fixture
def sample_blog_post() -> BlogPostData:
    return BlogPostData(
        slug="hello-world",
        title="Hello World",
        author="John Smith",
        content="First post.",
        tags=["intro"],
        published_at="2026-01-01",
    )


@pytest.fixture
def sample_user_profile() -> UserProfileData:
    return UserProfileData(
        user_id="u-99",
        username="johnsmith",
        email="john@example.com",
        bio="Loves Python.",
        join_date="2023-09-15",
        post_count=3,
    )


@pytest.fixture
def client() -> Iterator[FlaskClient]:
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client
