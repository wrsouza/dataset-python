"""URL patterns for the audit_trail_records app."""

from __future__ import annotations

from django.urls import path

from audit_trail_records.django_app.views import (
    create_product,
    product_history,
    undo_product,
    update_product,
)

app_name = "audit_trail_records"

urlpatterns = [
    path("products/", create_product, name="create"),
    path("products/<str:product_id>/", update_product, name="update"),
    path("products/<str:product_id>/undo/", undo_product, name="undo"),
    path("products/<str:product_id>/history/", product_history, name="history"),
]
