"""URL patterns for the catalog app."""

from __future__ import annotations

from django.urls import path

from catalog.views import FactoryStatsView, ProductListView

app_name = "catalog"

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/stats/", FactoryStatsView.as_view(), name="product-stats"),
]
