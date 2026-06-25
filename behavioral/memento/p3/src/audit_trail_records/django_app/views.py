"""HTTP views exposing the Model Audit Trail: create, update, undo, history."""

from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from audit_trail_records.application.use_cases import (
    CreateProductInput,
    CreateProductUseCase,
    GetAuditHistoryUseCase,
    UndoProductUseCase,
    UpdateProductInput,
    UpdateProductUseCase,
)
from audit_trail_records.domain.entities import (
    NoHistoryError,
    Product,
    ProductNotFoundError,
    ProductSnapshot,
)
from audit_trail_records.infrastructure.caretaker import DjangoAuditTrailCaretaker
from audit_trail_records.infrastructure.repository import DjangoProductRepository


def _product_to_dict(product: Product) -> dict[str, object]:
    return {
        "product_id": product.product_id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock,
        "current_version": product.current_version,
    }


def _snapshot_to_dict(snapshot: ProductSnapshot) -> dict[str, object]:
    return {
        "version": snapshot.version,
        "name": snapshot.name,
        "price": snapshot.price,
        "stock": snapshot.stock,
        "changed_by": snapshot.changed_by,
        "created_at": snapshot.created_at.isoformat(),
    }


def _repository() -> DjangoProductRepository:
    return DjangoProductRepository()


def _caretaker() -> DjangoAuditTrailCaretaker:
    return DjangoAuditTrailCaretaker()


@csrf_exempt
@require_http_methods(["POST"])
def create_product(request: HttpRequest) -> JsonResponse:
    """POST /products/ — create a product and its first audit snapshot."""
    payload = json.loads(request.body or "{}")
    use_case = CreateProductUseCase(_repository(), _caretaker())
    product = use_case.execute(
        CreateProductInput(
            product_id=payload["product_id"],
            name=payload["name"],
            price=payload["price"],
            stock=payload["stock"],
            changed_by=payload.get("changed_by", "system"),
        )
    )
    return JsonResponse(_product_to_dict(product), status=201)


@csrf_exempt
@require_http_methods(["PUT"])
def update_product(request: HttpRequest, product_id: str) -> JsonResponse:
    """PUT /products/<product_id>/ — edit a product and snapshot the change."""
    payload = json.loads(request.body or "{}")
    use_case = UpdateProductUseCase(_repository(), _caretaker())
    try:
        product = use_case.execute(
            UpdateProductInput(
                product_id=product_id,
                name=payload["name"],
                price=payload["price"],
                stock=payload["stock"],
                changed_by=payload.get("changed_by", "system"),
            )
        )
    except ProductNotFoundError as exc:
        return JsonResponse({"error": str(exc)}, status=404)
    return JsonResponse(_product_to_dict(product))


@csrf_exempt
@require_http_methods(["POST"])
def undo_product(request: HttpRequest, product_id: str) -> JsonResponse:
    """POST /products/<product_id>/undo/ — revert to the previous snapshot."""
    use_case = UndoProductUseCase(_repository(), _caretaker())
    try:
        product = use_case.execute(product_id)
    except (ProductNotFoundError, NoHistoryError) as exc:
        return JsonResponse({"error": str(exc)}, status=404)
    return JsonResponse(_product_to_dict(product))


@require_http_methods(["GET"])
def product_history(request: HttpRequest, product_id: str) -> JsonResponse:
    """GET /products/<product_id>/history/ — list all audit snapshots."""
    use_case = GetAuditHistoryUseCase(_caretaker())
    history = use_case.execute(product_id)
    return JsonResponse([_snapshot_to_dict(s) for s in history], safe=False)
