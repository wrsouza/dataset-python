"""Unit tests for the Composite pattern — Category Tree E-commerce.

No database required: pure in-memory trees built directly from
CategoryComposite and ProductLeaf.  Tests exercise 3+ nesting levels.
"""

from __future__ import annotations

from decimal import Decimal

from catalog.domain.interfaces import CatalogItem, ProductData
from catalog.infrastructure.composite import CategoryComposite, ProductLeaf

# ── Helpers ───────────────────────────────────────────────────────────────────


def make_product(
    sku: str = "SKU-001",
    name: str = "Test Product",
    price: str = "10.00",
    stock_qty: int = 5,
    category_id: int | None = 1,
) -> ProductLeaf:
    return ProductLeaf(
        name=name,
        price=Decimal(price),
        sku=sku,
        stock_qty=stock_qty,
        category_id=category_id,
        product_id=None,
    )


def make_category(
    category_id: int = 1,
    name: str = "Test Category",
    slug: str = "test-cat",
    parent_id: int | None = None,
) -> CategoryComposite:
    return CategoryComposite(
        category_id=category_id,
        name=name,
        slug=slug,
        parent_id=parent_id,
    )


def build_three_level_tree() -> CategoryComposite:
    """
    Electronics (L1)
      └── Smartphones (L2)
            ├── Android (L3) — 2 products
            └── iOS (L3)    — 1 product
    """
    p1 = make_product("AND-001", "Pixel 8", "699.99", 10, category_id=3)
    p2 = make_product("AND-002", "Galaxy S24", "999.99", 5, category_id=3)
    p3 = make_product("IOS-001", "iPhone 15", "799.99", 8, category_id=4)

    android = make_category(3, "Android", "android", parent_id=2)
    android.add_child(p1)
    android.add_child(p2)

    ios = make_category(4, "iOS", "ios", parent_id=2)
    ios.add_child(p3)

    smartphones = make_category(2, "Smartphones", "smartphones", parent_id=1)
    smartphones.add_child(android)
    smartphones.add_child(ios)

    electronics = make_category(1, "Electronics", "electronics")
    electronics.add_child(smartphones)

    return electronics


# ── ProductLeaf tests ─────────────────────────────────────────────────────────


class TestProductLeaf:
    def test_product_count_is_one(self) -> None:
        leaf = make_product()
        assert leaf.get_product_count() == 1

    def test_get_all_products_returns_self(self) -> None:
        leaf = make_product(sku="SKU-X", name="Gadget", price="49.99", stock_qty=3)
        products = leaf.get_all_products()
        assert len(products) == 1
        assert products[0].sku == "SKU-X"
        assert products[0].name == "Gadget"

    def test_total_value_equals_price_times_stock(self) -> None:
        leaf = make_product(price="25.00", stock_qty=4)
        assert leaf.calculate_total_value() == Decimal("100.00")

    def test_to_dict_contains_required_fields(self) -> None:
        leaf = make_product(sku="D001", name="Widget", price="9.99", stock_qty=10)
        d = leaf.to_dict()
        assert d["type"] == "product"
        assert d["sku"] == "D001"
        assert d["name"] == "Widget"
        assert d["stock_qty"] == 10

    def test_to_dict_depth_is_propagated(self) -> None:
        leaf = make_product()
        assert leaf.to_dict(depth=3)["depth"] == 3

    def test_zero_stock_value_is_zero(self) -> None:
        leaf = make_product(price="99.99", stock_qty=0)
        assert leaf.calculate_total_value() == Decimal("0")

    def test_product_data_repr(self) -> None:
        pd = ProductData("Widget", Decimal("9.99"), "W-001", 5, 1)
        assert "W-001" in repr(pd)


# ── CategoryComposite tests ───────────────────────────────────────────────────


class TestCategoryComposite:
    def test_empty_category_product_count_is_zero(self) -> None:
        cat = make_category()
        assert cat.get_product_count() == 0

    def test_empty_category_total_value_is_zero(self) -> None:
        cat = make_category()
        assert cat.calculate_total_value() == Decimal("0")

    def test_empty_category_all_products_is_empty(self) -> None:
        cat = make_category()
        assert cat.get_all_products() == []

    def test_single_product_child(self) -> None:
        cat = make_category()
        cat.add_child(make_product(price="50.00", stock_qty=2))
        assert cat.get_product_count() == 1
        assert cat.calculate_total_value() == Decimal("100.00")

    def test_multiple_product_children(self) -> None:
        cat = make_category()
        cat.add_child(make_product("A", price="10.00", stock_qty=3))
        cat.add_child(make_product("B", price="20.00", stock_qty=2))
        assert cat.get_product_count() == 2
        assert cat.calculate_total_value() == Decimal("70.00")

    def test_remove_child(self) -> None:
        cat = make_category()
        p = make_product()
        cat.add_child(p)
        cat.remove_child(p)
        assert cat.get_product_count() == 0

    def test_get_children_returns_copy(self) -> None:
        cat = make_category()
        p = make_product()
        cat.add_child(p)
        children = cat.get_children()
        children.clear()
        assert cat.get_product_count() == 1

    def test_slug_and_name_properties(self) -> None:
        cat = make_category(name="Gadgets", slug="gadgets")
        assert cat.slug == "gadgets"
        assert cat.name == "Gadgets"

    def test_to_dict_includes_children(self) -> None:
        cat = make_category(name="Root", slug="root")
        child = make_category(2, "Child", "child", parent_id=1)
        child.add_child(make_product())
        cat.add_child(child)
        d = cat.to_dict()
        assert d["type"] == "category"
        assert len(d["children"]) == 1
        assert d["children"][0]["slug"] == "child"


# ── Three-level recursive tests ───────────────────────────────────────────────


class TestThreeLevelTree:
    """Core Composite tests: 3-level tree — Electronics > Smartphones > Android/iOS."""

    def setup_method(self) -> None:
        self.root = build_three_level_tree()

    def test_product_count_sums_all_leaves(self) -> None:
        # Android: 2, iOS: 1 → total 3
        assert self.root.get_product_count() == 3

    def test_get_all_products_returns_flat_list(self) -> None:
        products = self.root.get_all_products()
        assert len(products) == 3
        skus = {p.sku for p in products}
        assert skus == {"AND-001", "AND-002", "IOS-001"}

    def test_total_value_recursive(self) -> None:
        # (699.99*10) + (999.99*5) + (799.99*8)
        expected = (
            Decimal("699.99") * 10 + Decimal("999.99") * 5 + Decimal("799.99") * 8
        )
        assert self.root.calculate_total_value() == expected

    def test_to_dict_has_correct_depth(self) -> None:
        d = self.root.to_dict(depth=0)
        smartphones = d["children"][0]
        android = smartphones["children"][0]
        product = android["children"][0]

        assert d["depth"] == 0
        assert smartphones["depth"] == 1
        assert android["depth"] == 2
        assert product["depth"] == 3

    def test_subtree_product_count(self) -> None:
        # Smartphones contains all 3 products
        smartphones = self.root.get_children()[0]
        assert smartphones.get_product_count() == 3

    def test_leaf_subtree_product_count(self) -> None:
        smartphones = self.root.get_children()[0]
        assert isinstance(smartphones, CategoryComposite)
        android = smartphones.get_children()[0]
        ios = smartphones.get_children()[1]
        assert android.get_product_count() == 2
        assert ios.get_product_count() == 1

    def test_lsp_treat_leaf_and_composite_uniformly(self) -> None:
        """LSP: any CatalogItem can be placed in a list and operated on uniformly."""
        electronics = self.root
        smartphones = self.root.get_children()[0]
        assert isinstance(smartphones, CategoryComposite)
        android = smartphones.get_children()[0]

        # Treat root, mid-node, and leaf subtree as the same interface
        items: list[CatalogItem] = [electronics, smartphones, android]
        counts = [item.get_product_count() for item in items]
        assert counts == [3, 3, 2]

    def test_ocp_add_new_category_without_modifying_existing(self) -> None:
        """OCP: adding Tablets under Electronics requires no change to existing code."""
        tablets = make_category(5, "Tablets", "tablets", parent_id=1)
        tablets.add_child(make_product("TAB-001", "iPad Pro", "1099.99", 20))
        self.root.add_child(tablets)

        # Root now has Smartphones + Tablets → 4 products
        assert self.root.get_product_count() == 4


# ── Deep nesting test (4 levels) ─────────────────────────────────────────────


class TestDeepNesting:
    def test_four_level_tree_recursion(self) -> None:
        """Verify recursive operations work at 4 levels of nesting."""
        leaf = make_product("DEEP-001", "Deep Product", "100.00", 1)

        l4 = make_category(4, "L4", "l4", parent_id=3)
        l4.add_child(leaf)
        l3 = make_category(3, "L3", "l3", parent_id=2)
        l3.add_child(l4)
        l2 = make_category(2, "L2", "l2", parent_id=1)
        l2.add_child(l3)
        l1 = make_category(1, "L1", "l1")
        l1.add_child(l2)

        assert l1.get_product_count() == 1
        assert l1.calculate_total_value() == Decimal("100.00")
        assert len(l1.get_all_products()) == 1
        assert l1.get_all_products()[0].sku == "DEEP-001"
