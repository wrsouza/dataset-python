"""URL patterns for the catalog app."""

from __future__ import annotations

from django.urls import path

from catalog.views import (
    CategoryDetailView,
    CategoryListView,
    CategoryProductsView,
    CategoryStatsView,
)

app_name = "catalog"

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path(
        "categories/<slug:slug>/", CategoryDetailView.as_view(), name="category-detail"
    ),
    path(
        "categories/<slug:slug>/products/",
        CategoryProductsView.as_view(),
        name="category-products",
    ),
    path(
        "categories/<slug:slug>/stats/",
        CategoryStatsView.as_view(),
        name="category-stats",
    ),
]
