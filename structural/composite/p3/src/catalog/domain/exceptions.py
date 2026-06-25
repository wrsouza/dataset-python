"""Domain exceptions for the catalog bounded context."""

from __future__ import annotations


class CatalogItemNotFoundError(Exception):
    """Raised when a requested category or product does not exist."""

    def __init__(self, slug: str) -> None:
        self.slug = slug
        super().__init__(f"Catalog item not found: {slug!r}")


class DuplicateSlugError(Exception):
    """Raised when a category slug already exists in the tree."""

    def __init__(self, slug: str) -> None:
        self.slug = slug
        super().__init__(f"Slug already exists: {slug!r}")
