"""Django views for the products API.

Views are thin: they parse HTTP, delegate to use cases, and format responses.
Business logic lives in use cases and domain prototypes.
"""
from __future__ import annotations

import json
from typing import Any

from django.http import HttpRequest, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from products.application.use_cases import (
    CloneProductUseCase,
    ListTemplatesUseCase,
    ListVariantsUseCase,
)
from products.domain.entities import ProductNotFoundError
from products.infrastructure.models import ProductModel
from products.infrastructure.prototypes import build_default_registry

# Composition root: registry is shared across views
_registry = build_default_registry()


@method_decorator(csrf_exempt, name="dispatch")
class ProductTemplatesView(View):
    """GET /products/templates/ — list all product template keys."""

    def get(self, request: HttpRequest) -> JsonResponse:
        use_case = ListTemplatesUseCase(_registry)
        templates = use_case.execute()
        return JsonResponse({"templates": templates})


@method_decorator(csrf_exempt, name="dispatch")
class CloneProductView(View):
    """POST /products/clone/<product_id>/ — clone a product with overrides."""

    def post(self, request: HttpRequest, product_id: int) -> JsonResponse:
        try:
            parent = ProductModel.objects.get(pk=product_id, is_template=True)
        except ProductModel.DoesNotExist:
            return JsonResponse(
                {"error": f"Template product with id={product_id} not found"},
                status=404,
            )

        body: dict[str, Any] = {}
        if request.body:
            try:
                body = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON body"}, status=400)

        overrides: dict[str, Any] = body.get("overrides", {})
        template_key: str = parent.sku  # sku acts as registry key for DB templates

        # Fall back to the registry's in-memory key if needed
        try:
            _registry.get(template_key)
        except ProductNotFoundError:
            # Use the product_type-based default key
            default_keys = {
                "physical": "tshirt-basic",
                "digital": "ebook-python",
                "subscription": "saas-starter",
            }
            template_key = default_keys.get(parent.product_type, "tshirt-basic")

        use_case = CloneProductUseCase(_registry)
        variant = use_case.execute(template_key, overrides, product_id)

        return JsonResponse(
            {
                "id": variant.id,
                "parent_product_id": variant.parent_product_id,
                "sku": variant.sku,
                "name": variant.name,
                "base_price": variant.base_price,
                "product_type": variant.product_type,
                "extra_attrs": variant.extra_attrs,
            },
            status=201,
        )


@method_decorator(csrf_exempt, name="dispatch")
class ProductVariantsView(View):
    """GET /products/<product_id>/variants/ — list all variants."""

    def get(self, request: HttpRequest, product_id: int) -> JsonResponse:
        if not ProductModel.objects.filter(pk=product_id).exists():
            return JsonResponse(
                {"error": f"Product with id={product_id} not found"},
                status=404,
            )

        use_case = ListVariantsUseCase()
        variants = use_case.execute(product_id)
        return JsonResponse(
            {
                "product_id": product_id,
                "variants": [
                    {
                        "id": v.id,
                        "sku": v.sku,
                        "name": v.name,
                        "base_price": v.base_price,
                        "extra_attrs": v.extra_attrs,
                    }
                    for v in variants
                ],
            }
        )
