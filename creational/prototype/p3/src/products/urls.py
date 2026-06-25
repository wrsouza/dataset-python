"""URL configuration for the products app."""
from __future__ import annotations

from django.urls import path

from products.views.product_views import (
    CloneProductView,
    ProductTemplatesView,
    ProductVariantsView,
)

urlpatterns = [
    path("products/templates/", ProductTemplatesView.as_view(), name="product-templates"),
    path("products/clone/<int:product_id>/", CloneProductView.as_view(), name="clone-product"),
    path("products/<int:product_id>/variants/", ProductVariantsView.as_view(), name="product-variants"),
]
