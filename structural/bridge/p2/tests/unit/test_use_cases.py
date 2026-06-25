"""Unit tests for RenderPageUseCase."""

from __future__ import annotations

import pytest

from renderer.application.use_cases import PageNotFoundError, RenderPageUseCase
from renderer.infrastructure.implementations import JSONRenderer


@pytest.fixture
def use_case() -> RenderPageUseCase:
    return RenderPageUseCase()


def test_render_product_returns_serialized_body(use_case: RenderPageUseCase) -> None:
    result = use_case.render_product("p-100", JSONRenderer())
    assert "Mechanical Keyboard" in result


def test_render_product_unknown_id_raises(use_case: RenderPageUseCase) -> None:
    with pytest.raises(PageNotFoundError):
        use_case.render_product("missing", JSONRenderer())


def test_render_blog_post_returns_serialized_body(use_case: RenderPageUseCase) -> None:
    result = use_case.render_blog_post("bridge-pattern-explained", JSONRenderer())
    assert "The Bridge Pattern Explained" in result


def test_render_blog_post_unknown_slug_raises(use_case: RenderPageUseCase) -> None:
    with pytest.raises(PageNotFoundError):
        use_case.render_blog_post("missing", JSONRenderer())


def test_render_user_profile_returns_serialized_body(
    use_case: RenderPageUseCase,
) -> None:
    result = use_case.render_user_profile("u-1", JSONRenderer())
    assert "janedoe" in result


def test_render_user_profile_unknown_id_raises(use_case: RenderPageUseCase) -> None:
    with pytest.raises(PageNotFoundError):
        use_case.render_user_profile("missing", JSONRenderer())
