"""Repository: loads Django ORM records and builds the Composite tree.

Keeps ORM concerns out of domain objects (SRP).
The tree builder converts ORM adjacency-list rows into the in-memory
Composite structure without any business logic.
"""

from __future__ import annotations

from catalog.infrastructure.composite import CategoryComposite, ProductLeaf
from catalog.models import Category


def _build_subtree(category: Category) -> CategoryComposite:
    """Recursively convert an ORM Category (with prefetched data) into a Composite.

    Recursion depth matches the category tree depth — for a 3-level
    e-commerce tree this is trivially safe.
    """
    node = CategoryComposite(
        category_id=category.pk,
        name=category.name,
        slug=category.slug,
        parent_id=category.parent_id,
    )

    for product in category.products.all():
        node.add_child(
            ProductLeaf(
                name=product.name,
                price=product.price,
                sku=product.sku,
                stock_qty=product.stock_qty,
                category_id=product.category_id,
                product_id=product.pk,
            )
        )

    for child_category in category.children.all():
        node.add_child(_build_subtree(child_category))

    return node


def build_full_catalog_tree() -> list[CategoryComposite]:
    """Return one Composite per root category (parent=None).

    Uses select_related + prefetch_related to avoid N+1 queries.
    """
    roots = Category.objects.filter(parent__isnull=True).prefetch_related(
        "products",
        "children__products",
        "children__children__products",
        "children__children__children__products",
    )
    return [_build_subtree(root) for root in roots]


def build_subtree_by_slug(slug: str) -> CategoryComposite | None:
    """Return the composite subtree rooted at the given slug, or None."""
    try:
        category = Category.objects.prefetch_related(
            "products",
            "children__products",
            "children__children__products",
            "children__children__children__products",
        ).get(slug=slug)
    except Category.DoesNotExist:
        return None
    return _build_subtree(category)
