"""Unit tests for product use cases using mocks."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from products.application.use_cases import ListTemplatesUseCase
from products.domain.interfaces import ProductRegistry
from products.infrastructure.prototypes import build_default_registry


class TestListTemplatesUseCase:
    def test_returns_registry_templates(self) -> None:
        registry = build_default_registry()
        use_case = ListTemplatesUseCase(registry)
        templates = use_case.execute()
        assert isinstance(templates, list)
        assert len(templates) == 3

    def test_uses_registry_interface(self) -> None:
        mock_registry: ProductRegistry = MagicMock(spec=ProductRegistry)
        mock_registry.list_templates.return_value = ["a", "b"]
        use_case = ListTemplatesUseCase(mock_registry)
        result = use_case.execute()
        assert result == ["a", "b"]
        mock_registry.list_templates.assert_called_once()
