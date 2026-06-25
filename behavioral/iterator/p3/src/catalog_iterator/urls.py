"""URL patterns for the catalog_iterator app."""

from __future__ import annotations

from django.urls import path

from catalog_iterator.views import CategorySummaryView, ProductListView

app_name = "catalog_iterator"

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path(
        "products/category-summary/",
        CategorySummaryView.as_view(),
        name="category-summary",
    ),
]
